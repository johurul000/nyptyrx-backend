from django.test import TestCase

# Create your tests here.

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode
from django.db import transaction
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Invoice, PharmacyStock
from .serializers import InvoiceSerializer, InvoiceItemSerializer
from rest_framework.permissions import IsAuthenticated

class CreateInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the invoice data and items from the request
        user = request.user  # Authenticated user
        pharmacy = user.pharmacy

        invoice_data = {
            key: value
            for key, value in request.data.items()
            if key != "items"  # Exclude items for now
        }

        # Converting to Decimal
        invoice_data['subtotal'] = Decimal(request.data.get('subtotal', 0.0))
        invoice_data['discount_percentage'] = Decimal(request.data.get('discount_percentage', 0.0))
        invoice_data['tax_percentage'] = Decimal(request.data.get('tax_percentage', 0.0))
        invoice_data['total'] = Decimal(request.data.get('total', 0.0))

        items_data = request.data.get("items", [])

        if not items_data:
            return Response(
                {"error": "Invoice must have at least one item."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Add the user and pharmacy to the invoice data
        invoice_data["user"] = user.id
        invoice_data["pharmacy"] = pharmacy.id

        # Wrap the operation in a transaction to ensure atomicity
        with transaction.atomic():
            # Serialize and save the invoice
            invoice = Invoice(
                user=user,
                pharmacy=pharmacy,
                customer_name=invoice_data['customer_name'],
                customer_email=invoice_data.get('customer_email', ''),
                customer_phone=invoice_data.get('customer_phone', ''),
                pharmacy_name=invoice_data['pharmacy_name'],
                pharmacy_email=invoice_data.get('pharmacy_email', ''),
                pharmacy_phone=invoice_data.get('pharmacy_phone', ''),
                subtotal=invoice_data['subtotal'],
                discount_percentage=invoice_data['discount_percentage'],
                tax_percentage=invoice_data['tax_percentage'],
                total=invoice_data['total'],
            )

            try:
                invoice.save()
            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": f"Error saving invoice: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Serialize and save the invoice items
            for item_data in items_data:
                medicine_name = item_data.get("medicine_name")
                quantity = item_data.get("quantity")

                try:
                    stock = PharmacyStock.objects.get(
                        pharmacy=invoice.pharmacy, medicine_name=medicine_name
                    )
                except PharmacyStock.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response(
                        {"error": f"Medicine '{medicine_name}' is not available in stock."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if stock.quantity < quantity:
                    transaction.set_rollback(True)
                    return Response(
                        {"error": f"Not enough stock for '{medicine_name}'. Available: {stock.quantity}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Deduct stock quantity
                stock.quantity -= quantity
                stock.save()

                # Add the invoice reference to the item data
                item_data["invoice"] = invoice.id
                item_serializer = InvoiceItemSerializer(data=item_data)
                if not item_serializer.is_valid():
                    transaction.set_rollback(True)
                    return Response(
                        item_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
                item_serializer.save()

            # Construct the invoice URL (assuming you have set up a URL pattern for the invoice page)
            invoice_url = f"http://localhost:3000/invoice/{invoice.id}"

            # Send an email to the customer with the invoice link
            send_mail(
                subject=f"Your Invoice from {invoice.pharmacy_name}",
                message=f"Dear {invoice.customer_name},\n\nYour invoice has been created. You can view it by following this link: {invoice_url}\n\nThank you for your business!",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[invoice.customer_email],
                fail_silently=False,
            )

            # Return the created invoice with nested items
            return Response(
                InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED
            )

