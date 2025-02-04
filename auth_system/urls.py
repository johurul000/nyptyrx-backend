from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from .views import *

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('get-user/', GetUserAPIView.as_view(), name='get-user'),
    path('users/<int:user_id>/edit/', EditUserAPIView.as_view(), name='edit_user_details'),

    path('create-pharmacy/', CreatePharmacyView.as_view(), name='create-pharmacy'),
    path('edit-pharmacy/<int:pharmacy_id>/', EditPharmacyView.as_view(), name='edit-pharmacy'),
    path('pharmacy-details/<int:pharmacy_id>/', GetPharmacyView.as_view(), name='pharmacy-details'),


    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_view'),
]


# bg #1E293B
# card #0F172A
# highlight #2563EB
# highlight-hover #1D4ED8
