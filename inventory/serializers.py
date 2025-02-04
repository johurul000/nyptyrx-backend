from rest_framework import serializers
from .models import CentralMedicine, MedicineCategory, PharmacyMedicine, PharmacyStock, Invoice, InvoiceItem

# Serializer for CentralMedicine
class CentralMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentralMedicine
        fields = [
            'id',
            'name',
            'description',
            'price',
            'is_discontinued',
            'manufacturer_name',
            'medicine_type',
            'pack_size_label',
            'short_composition1',
            'short_composition2',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Serializer for MedicineCategory
class MedicineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineCategory
        fields = [
            'id',
            'name',
            'description',
        ]
        read_only_fields = ['id']


# Serializer for PharmacyMedicine
class PharmacyMedicineSerializer(serializers.ModelSerializer):
    central_medicine = CentralMedicineSerializer(read_only=True)  # Nested serializer for central medicine
    central_medicine_id = serializers.PrimaryKeyRelatedField(
        queryset=CentralMedicine.objects.all(), source='central_medicine', write_only=True
    )

    class Meta:
        model = PharmacyMedicine
        fields = [
            'id',
            'pharmacy',
            'central_medicine',
            'central_medicine_id',
            'price',
            'custom_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Serializer for PharmacyStock
class PharmacyStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyStock
        fields = [
            'id',
            'user',
            'pharmacy',
            'central_medicine',
            'medicine_name',
            'description',
            'price',
            'manufacturer_name',
            'medicine_type',
            'pack_size_label',
            'short_composition1',
            'short_composition2',
            'quantity',
            'threshold',
            'batch_number',
            'expiry_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']



class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = [
            'id',
            'invoice',
            'medicine_name',
            'quantity',
            'price',
            'total',
        ]
        read_only_fields = ['id', 'total']  # `total` is calculated automatically in the model


class InvoiceSerializer(serializers.ModelSerializer):
    # Use the InvoiceItemSerializer for the related items
    items = InvoiceItemSerializer(many=True, read_only=True)  # Nested serialization for related items

    class Meta:
        model = Invoice
        fields = [
            'id',
            'user',
            'pharmacy',
            'invoice_number',
            'date',
            'customer_name',
            'customer_email',
            'customer_phone',
            'pharmacy_name',
            'pharmacy_email',
            'pharmacy_phone',
            'subtotal',
            'discount_percentage',
            'tax_percentage',
            'total',
            'items',  # Include related InvoiceItem objects
        ]
        read_only_fields = ['id', 'invoice_number', 'subtotal', 'total', 'items']  # Read-only fields