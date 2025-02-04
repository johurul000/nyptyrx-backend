from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q

from auth_system.models import Pharmacy
from .models import *
from .serializers import *
from django.db import transaction, DatabaseError
from decimal import Decimal


from datetime import timedelta, date, datetime
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth, Coalesce
from collections import defaultdict
# Create your views here.

class SearchCentralMedicineView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Search query is missing."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter medicines using case-insensitive partial matching
        medicines = CentralMedicine.objects.filter(
            Q(name__icontains=query) |
            Q(short_composition1__icontains=query) |
            Q(short_composition2__icontains=query)
        )[:10]  # Limit the results for better performance
        
        serializer = CentralMedicineSerializer(medicines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddMedicineToInventoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        pharmacy_id = kwargs.get("pharmacy_id")  # Pharmacy ID from the URL
        try:
            pharmacy = Pharmacy.objects.get(id=pharmacy_id, created_by=request.user)
        except Pharmacy.DoesNotExist:
            return Response(
                {"error": "Pharmacy not found or access denied."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Attach the pharmacy to the request data
        data = request.data
        data['pharmacy'] = pharmacy.id
        data['user'] = request.user.id

        serializer = PharmacyStockSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Medicine added to inventory successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditMedicineInInventoryView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pharmacy_id, medicine_id, *args, **kwargs):
        """
        Update an existing medicine in the pharmacy's inventory.
        """
        try:
            # Ensure the authenticated user has access to this pharmacy
            pharmacy = Pharmacy.objects.get(id=pharmacy_id, created_by=request.user)
        except Pharmacy.DoesNotExist:
            return Response(
                {"error": "Pharmacy not found or access denied."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the medicine exists in the inventory and belongs to the pharmacy
        medicine = get_object_or_404(PharmacyStock, id=medicine_id, pharmacy=pharmacy)

        # Update the medicine with the provided data
        serializer = PharmacyStockSerializer(medicine, data=request.data, partial=True)  # `partial=True` for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Medicine updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PharmacyStockListView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve all PharmacyStock objects
        pharmacy_stocks = PharmacyStock.objects.filter(pharmacy=request.user.pharmacy)
        # Serialize the data
        serializer = PharmacyStockSerializer(pharmacy_stocks, many=True)
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class SearchPharmacyStockView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Search query is missing."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        stock = PharmacyStock.objects.filter(
            pharmacy=request.user.pharmacy
        ).filter(
            Q(medicine_name__icontains=query) |
            Q(short_composition1__icontains=query) |
            Q(short_composition2__icontains=query)
        )[:10]  
        
        serializer = PharmacyStockSerializer(stock, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CreateInvoiceView(APIView):
    """
    API endpoint to create an invoice with nested invoice items and update pharmacy stock.
    """
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

        if pharmacy:
            invoice_data['pharmacy_name'] = pharmacy.name
            invoice_data['pharmacy_email'] = pharmacy.email
            invoice_data['pharmacy_phone'] = pharmacy.phone
        else:
            # Optional: Handle cases where pharmacy information is missing (e.g., for admin or users without a pharmacy)
            invoice_data['pharmacy_name'] = ''
            invoice_data['pharmacy_email'] = ''
            invoice_data['pharmacy_phone'] = ''

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

        # Save the invoice
            try:
                invoice.save()
            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": f"Error saving invoice: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

            # Serialize and save the invoice items
            for item_data in items_data:
                # Check stock availability
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

        # Return the created invoice with nested items
        return Response(
            InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED
        )
    

class InvoiceDetailView(APIView):
    """
    API endpoint to fetch an invoice and its associated items by invoice number.
    """

    permission_classes = [AllowAny]

    def get(self, request, invoice_number, *args, **kwargs):
        try:
            # Fetch the invoice by the provided invoice_number
            invoice = Invoice.objects.get(invoice_number=invoice_number)
            
            # Serialize the invoice data
            serializer = InvoiceSerializer(invoice)

            # Return the serialized invoice data
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Invoice.DoesNotExist:
            # If the invoice is not found, return a 404 error
            return Response(
                {"error": "Invoice not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        


class PharmacyMetricsViewSet(viewsets.ViewSet):

    def list(self, request):
        try:
            # Ensure the user is authenticated and has an associated pharmacy
            if not hasattr(request.user, 'pharmacy'):
                return Response(
                    {'error': 'User is not associated with any pharmacy.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            pharmacy = request.user.pharmacy

            # Metrics
            total_inventory = PharmacyStock.objects.filter(pharmacy=pharmacy).count()
            total_stock_value = sum(
                stock.price * stock.quantity for stock in PharmacyStock.objects.filter(pharmacy=pharmacy)
            )
            out_of_stock = PharmacyStock.objects.filter(pharmacy=pharmacy, quantity=0).count()
            expiring_medicines = PharmacyStock.objects.filter(
                pharmacy=pharmacy, expiry_date__lte=date.today() + timedelta(days=30)
            ).count()


            total_invoices = Invoice.objects.filter(pharmacy=pharmacy).count()

            total_sales = sum(invoice.total if invoice.total is not None else 0 for invoice in Invoice.objects.filter(pharmacy=pharmacy))


            low_stock_medicines = PharmacyStock.objects.filter(
                pharmacy=pharmacy, quantity__lte=F('threshold')
            ).count()


            today = date.today()
            daily_earnings = Invoice.objects.filter(
                pharmacy=pharmacy, date=today
            ).aggregate(total=Sum('total'))['total'] or 0

            daily_invoices_processed = Invoice.objects.filter(
                pharmacy=pharmacy, date=today
            ).count()

            current_month = datetime.now().month
            current_year = datetime.now().year

            monthly_earnings = Invoice.objects.filter(
                pharmacy=pharmacy, date__month=current_month, date__year=current_year
            ).aggregate(total=Sum('total'))['total'] or 0

            monthly_invoices_processed = Invoice.objects.filter(
                pharmacy=pharmacy, date__month=current_month, date__year=current_year
            ).count()


            weekly_sales = []
            labels = []

            for i in range(6, -1, -1):  # Loop from 6 days ago to today
                day = today - timedelta(days=i)
                labels.append(day.strftime("%A"))  # Get day name (Monday, Tuesday, etc.)
                sales = Invoice.objects.filter(pharmacy=pharmacy, date=day).aggregate(total=Sum('total'))['total'] or 0
                weekly_sales.append(sales)

            weekly_revenue = []
            week_labels = []
            for i in range(4):
                week_start = today - timedelta(days=today.weekday() + (i * 7))  # Start of the week
                week_end = week_start + timedelta(days=6)  # End of the week
                week_labels.append(f"Week {4 - i}")  # Generate week labels (Week 4, Week 3, ...)

                total_weekly_revenue = Invoice.objects.filter(
                    pharmacy=pharmacy, date__range=[week_start, week_end]
                ).aggregate(total=Sum('total'))['total'] or 0
                
                weekly_revenue.append(total_weekly_revenue)

            monthly_revenue = []
            month_labels = []

            for i in range(6, 0, -1):  # Iterate from 6 months ago to current month
                month = (today.month - i) % 12 or 12  # Get correct month number
                year = today.year if today.month - i > 0 else today.year - 1  # Adjust year

                month_name = datetime(year, month, 1).strftime("%B")  # Get month name
                month_labels.append(month_name)

                total_monthly_revenue = Invoice.objects.filter(
                    pharmacy=pharmacy, date__month=month, date__year=year
                ).aggregate(total=Sum('total'))['total'] or 0

                monthly_revenue.append(total_monthly_revenue)


            top_selling_products = (
                InvoiceItem.objects.filter(invoice__pharmacy=pharmacy)
                .values("medicine_name")  # Group by medicine name
                .annotate(
                    total_units=Sum("quantity"),  # Sum total quantity sold
                    total_revenue=Sum("total")  # Sum total revenue
                )
                .order_by("-total_units")[:5]  # Order by highest sales and limit to top 5
            )

            top_selling_products_data = list(top_selling_products)



            low_stock_medicines_list = (
                PharmacyStock.objects.filter(pharmacy=pharmacy, quantity__lte=F('threshold'))
                .values("medicine_name", "quantity")  # Select only needed fields
                .order_by("quantity")  # Sort by lowest stock first
            )

            # Convert QuerySet to list
            low_stock_medicines_data = list(low_stock_medicines_list)


            expiring_medicines_list = (
                PharmacyStock.objects.filter(
                    pharmacy=pharmacy, expiry_date__lte=date.today() + timedelta(days=30)
                )
                .values("medicine_name", "expiry_date")  # Select only the needed fields
                .order_by("expiry_date")  # Order by expiry date
            )

            # Convert QuerySet to list
            expiring_medicines_data = list(expiring_medicines_list)


            
            # Success Response
            return Response({
                'total_inventory': total_inventory,
                'total_stock_value': total_stock_value,
                'out_of_stock': out_of_stock,
                'expiring_medicines': expiring_medicines,
                'total_invoices': total_invoices,
                'total_sales': total_sales,
                'low_stock_medicines': low_stock_medicines,
                'daily_earnings': daily_earnings,
                'daily_invoices_processed': daily_invoices_processed,
                'monthly_earnings': monthly_earnings,
                'monthly_invoices_processed': monthly_invoices_processed,
                'weekly_sales': {
                    'labels': labels,
                    'data': weekly_sales
                },
                'weekly_revenue': {
                    'labels': week_labels[::-1],
                    'data': weekly_revenue[::-1]
                },
                'monthly_revenue': {
                    'labels': month_labels,
                    'data': monthly_revenue
                },
                'top_selling_products': top_selling_products_data,
                'low_stock_medicines_list': low_stock_medicines_data,
                'expiring_medicines_list': expiring_medicines_data,

            }, status=status.HTTP_200_OK)

        except DatabaseError as db_error:
            return Response(
                {'error': f'Database error: {str(db_error)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as ex:
            return Response(
                {'error': f'An unexpected error occurred: {str(ex)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the pharmacy associated with the authenticated user
        if not hasattr(request.user, 'pharmacy'):
            return Response(
                {'error': 'User is not associated with any pharmacy.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pharmacy = request.user.pharmacy

        # Get all invoices for the pharmacy
        invoices = Invoice.objects.filter(pharmacy=pharmacy)

        # Serialize the invoice data (use fields that you need)
        invoice_serializer = InvoiceSerializer(invoices, many=True)

        return Response(invoice_serializer.data, status=status.HTTP_200_OK)