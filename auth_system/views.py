from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import PharmacyUser, Pharmacy
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from rest_framework import status, exceptions


# Create your views here.

class GetUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = PharmacyUserSerializer(user)
        return Response(serializer.data, status=200)

class RegisterAPIView(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SimpleRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer


class EditUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user = PharmacyUser.objects.get(id=user_id)
        except PharmacyUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PharmacyUserSerializer(user, data=request.data, partial=True)  # Use partial=True for partial updates
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Pharmacy Views

class GetPharmacyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pharmacy_id, *args, **kwargs):
        # Fetch the pharmacy object or return 404 if not found
        pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
        
        # Serialize the pharmacy data
        serializer = PharmacySerializer(pharmacy)
        
        # Return serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePharmacyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PharmacyCreationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            pharmacy = serializer.save()
            return Response(
                {"message": "Pharmacy created successfully.", "pharmacy_id": pharmacy.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class EditPharmacyView(APIView):
    permission_classes = [IsAuthenticated]

    def get_pharmacy(self, user, pharmacy_id):
        try:
            pharmacy = Pharmacy.objects.get(id=pharmacy_id, created_by=user)
            return pharmacy
        except Pharmacy.DoesNotExist:
            raise exceptions.NotFound("Pharmacy not found or you do not have permission to edit it.")

    def put(self, request, pharmacy_id, *args, **kwargs):
        pharmacy = self.get_pharmacy(request.user, pharmacy_id)
        serializer = PharmacyEditSerializer(pharmacy, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Pharmacy updated successfully.", "pharmacy": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)