import uuid
from django.utils.timezone import now
from datetime import date, datetime
from django.db import models
from auth_system.models import Pharmacy, PharmacyUser
from decimal import Decimal
from django.db.models import Sum

# Create your models here.

# Central Medicines Table
class CentralMedicine(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the medicine
    is_discontinued = models.BooleanField(default=False)  # Whether the medicine is discontinued
    manufacturer_name = models.CharField(max_length=255)  # Manufacturer name
    medicine_type = models.CharField(max_length=255)  # Type (e.g., allopathy, homeopathy)
    pack_size_label = models.CharField(max_length=255)  # Pack size (e.g., strip of 10 tablets)
    short_composition1 = models.CharField(max_length=255, blank=True, null=True)  # Composition 1
    short_composition2 = models.CharField(max_length=255, blank=True, null=True)  # Composition 2
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

# Medicine Categories
class MedicineCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

# Pharmacy Medicines Table
class PharmacyMedicine(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    central_medicine = models.ForeignKey(CentralMedicine, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    custom_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.custom_name if self.custom_name else self.central_medicine.name

# Pharmacy Stock Table
class PharmacyStock(models.Model):
    user = models.ForeignKey(PharmacyUser, on_delete=models.CASCADE, blank=True, null=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    central_medicine = models.ForeignKey(CentralMedicine, on_delete=models.CASCADE, blank=True, null=True)
    
    # Additional fields for manual entry
    medicine_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    manufacturer_name = models.CharField(max_length=255, blank=True, null=True)
    medicine_type = models.CharField(max_length=255, blank=True, null=True)
    pack_size_label = models.CharField(max_length=255, blank=True, null=True)
    short_composition1 = models.CharField(max_length=255, blank=True, null=True)
    short_composition2 = models.CharField(max_length=255, blank=True, null=True)
    
    quantity = models.IntegerField()
    threshold = models.IntegerField(default=0)
    batch_number = models.CharField(max_length=255, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine_name} ({self.pharmacy.name})"
    
def short_uuid():
    return str(uuid.uuid4())[:13]

class Invoice(models.Model):
    user = models.ForeignKey(PharmacyUser, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=13, default=short_uuid, editable=False, unique=True)
    date = models.DateField(default=date.today)

    # Customer Details
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)

    # Business Details
    pharmacy_name = models.CharField(max_length=255)
    pharmacy_email = models.EmailField(blank=True, null=True)
    pharmacy_phone = models.CharField(max_length=15, blank=True, null=True)

    # Financial Fields
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name} | {self.pharmacy.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        # Automatically calculate the total for the item
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.medicine_name} (x{self.quantity})"

    
