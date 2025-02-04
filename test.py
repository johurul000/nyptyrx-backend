from django.db import models
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid



class Pharmacy(models.Model):
    name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.OneToOneField(
        'PharmacyUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_pharmacy'
    )

    def __str__(self):
        return self.name


class PharmacyUser(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_PHARMACIST = 'pharmacist'
    ROLE_MAINTAINER = 'maintainer'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_PHARMACIST, 'Pharmacist'),
        (ROLE_MAINTAINER, 'Maintainer'),
    ]
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, null=True, blank=True)

    # Custom related_name for 'groups' and 'user_permissions' to avoid reverse relationship clashes
    groups = models.ManyToManyField(
        Group,
        related_name='pharmacyuser_set',  # Custom reverse relation name
        blank=True,
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='pharmacyuser_permissions_set',  # Custom reverse relation name
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def save(self, *args, **kwargs):
        # Ensure superusers and maintainers do not have a pharmacy
        if self.is_superuser or self.role == 'maintainer':
            self.pharmacy = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role or 'Superuser'})"



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



            # Financial Data for Charts
            # Sales by month (total sales grouped by month)
            sales_by_month = Invoice.objects.filter(pharmacy=pharmacy) \
                .annotate(month_year=TruncMonth('date')) \
                .values('month_year') \
                .annotate(total_sales=Sum(Coalesce('total', 0))) \
                .order_by('month_year')
            




            # monthly_sales = defaultdict(float)
            # for record in sales_by_month:
            #     # Handle None values for total_sales
            #     month_year = record['month_year']
            #     formatted_month_year = f"{month_year.month:02d}-{month_year.year}"
            #     total_sales_value = record.get('total_sales', 0)
            #     monthly_sales[formatted_month_year] += total_sales_value


            # # Invoice Status (Paid vs Pending)
            # pending_invoices = Invoice.objects.filter(pharmacy=pharmacy, status='pending').count()
            # paid_invoices = Invoice.objects.filter(pharmacy=pharmacy, status='paid').count()

            
            # Success Response
            return Response({
                'total_inventory': total_inventory,
                'total_stock_value': total_stock_value,
                'out_of_stock': out_of_stock,
                'expiring_medicines': expiring_medicines,
                'total_invoices': total_invoices,
                'total_sales': total_sales,
                'low_stock_medicines': low_stock_medicines,
                # 'monthly_sales': monthly_sales,
                # 'paid_invoices': paid_invoices,
                # 'pending_invoices': pending_invoices
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
 