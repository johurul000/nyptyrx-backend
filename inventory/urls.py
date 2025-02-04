from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'metrics', PharmacyMetricsViewSet, basename='metrics')

urlpatterns = [
    path('central-medicine/search/', SearchCentralMedicineView.as_view(), name='search_medicine'),
    path('add-stock/<int:pharmacy_id>/', AddMedicineToInventoryView.as_view(), name='add-medicine-to-inventory'),
    path('edit-medicine/<int:pharmacy_id>/<int:medicine_id>/', EditMedicineInInventoryView.as_view(), name='edit-medicine-in-inventory'),
    path('pharmacy-stock/', PharmacyStockListView.as_view(), name='pharmacy-stock-list'),
    path('pharmacy-stock/search/', SearchPharmacyStockView.as_view(), name='pharmacy-stock-search'),
    path('create-invoice/', CreateInvoiceView.as_view(), name='create_invoice'),
    path('invoice/<str:invoice_number>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('', include(router.urls)), 

    path('get-invoices/', InvoiceListView.as_view(), name='get-invoices'),
]