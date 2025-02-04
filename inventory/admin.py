from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CentralMedicine)
admin.site.register(MedicineCategory)
admin.site.register(PharmacyMedicine)
admin.site.register(PharmacyStock)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)

