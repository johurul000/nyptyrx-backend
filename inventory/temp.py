# class CreateInvoiceView(APIView):
#     """
#     API endpoint to create an invoice with nested invoice items and update pharmacy stock.
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         # Extract the invoice data and items from the request

#         user = request.user  # Authenticated user
#         pharmacy = user.pharmacy

#         invoice_data = {
#             key: value
#             for key, value in request.data.items()
#             if key != "items"  # Exclude items for now
#         }

#         # Converting to Decimal
#         invoice_data['subtotal'] = Decimal(request.data.get('subtotal', 0.0))
#         invoice_data['discount_percentage'] = Decimal(request.data.get('discount_percentage', 0.0))
#         invoice_data['tax_percentage'] = Decimal(request.data.get('tax_percentage', 0.0))
#         invoice_data['total'] = Decimal(request.data.get('total', 0.0))

#         items_data = request.data.get("items", [])
        

#         if not items_data:
#             return Response(
#                 {"error": "Invoice must have at least one item."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
        
#         # Add the user and pharmacy to the invoice data
#         invoice_data["user"] = user.id
#         invoice_data["pharmacy"] = pharmacy.id
#         # print(invoice_data)
#         # print(items_data)

#         # Wrap the operation in a transaction to ensure atomicity
#         with transaction.atomic():

#             print(f"Before saving: Subtotal: {invoice_data['subtotal']}, Total: {invoice_data['total']}")


#             # Serialize and save the invoice
#             invoice_serializer = InvoiceSerializer(data=invoice_data)
#             if not invoice_serializer.is_valid():
#                 return Response(
#                     invoice_serializer.errors, status=status.HTTP_400_BAD_REQUEST
#                 )

#             invoice = invoice_serializer.save()
#             print(f"Saved Invoice: Subtotal: {invoice.subtotal}, Total: {invoice.total}")

#             # Serialize and save the invoice items
#             for item_data in items_data:
#                 # Check stock availability
#                 medicine_name = item_data.get("medicine_name")
#                 quantity = item_data.get("quantity")

#                 try:
#                     stock = PharmacyStock.objects.get(
#                         pharmacy=invoice.pharmacy, medicine_name=medicine_name
#                     )
#                 except PharmacyStock.DoesNotExist:
#                     transaction.set_rollback(True)
#                     return Response(
#                         {"error": f"Medicine '{medicine_name}' is not available in stock."},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 if stock.quantity < quantity:
#                     transaction.set_rollback(True)
#                     return Response(
#                         {"error": f"Not enough stock for '{medicine_name}'. Available: {stock.quantity}."},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # Deduct stock quantity
#                 stock.quantity -= quantity
#                 stock.save()

#                 # Add the invoice reference to the item data
#                 item_data["invoice"] = invoice.id
#                 item_serializer = InvoiceItemSerializer(data=item_data)
#                 if not item_serializer.is_valid():
#                     transaction.set_rollback(True)
#                     return Response(
#                         item_serializer.errors, status=status.HTTP_400_BAD_REQUEST
#                     )
#                 item_serializer.save()

#         # Return the created invoice with nested items
#         return Response(
#             InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED
#         )
    

# class InvoiceDetailView(APIView):
#     """
#     API endpoint to fetch an invoice and its associated items by invoice number.
#     """

#     permission_classes = [AllowAny]

#     def get(self, request, invoice_number, *args, **kwargs):
#         try:
#             # Fetch the invoice by the provided invoice_number
#             invoice = Invoice.objects.get(invoice_number=invoice_number)
            
#             # Serialize the invoice data
#             serializer = InvoiceSerializer(invoice)

#             # Return the serialized invoice data
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Invoice.DoesNotExist:
#             # If the invoice is not found, return a 404 error
#             return Response(
#                 {"error": "Invoice not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )