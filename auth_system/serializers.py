from rest_framework import serializers
from .models import Pharmacy, PharmacyUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator


class PharmacySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Pharmacy
        fields = [
            'id',
            'name',
            'owner_name',
            'email',
            'phone',
            'address',
            'created_at',
            'updated_at',
            'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        user = self.context['request'].user
        if hasattr(user, 'owned_pharmacy') and user.owned_pharmacy is not None:
            raise serializers.ValidationError("You already own a pharmacy.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        pharmacy = Pharmacy.objects.create(created_by=user, **validated_data)
        return pharmacy
    
class PharmacyCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = [
            'id',
            'name',
            'owner_name',
            'email',
            'phone',
            'address',
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        if hasattr(user, 'owned_pharmacy') and user.owned_pharmacy is not None:
            raise serializers.ValidationError("You already own a pharmacy.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        pharmacy = Pharmacy.objects.create(created_by=user, **validated_data)

        user.pharmacy = pharmacy
        user.save()
        
        return pharmacy


class PharmacyEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = [
            'id',
            'name',
            'owner_name',
            'email',
            'phone',
            'address',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        user = self.context['request'].user
        pharmacy = self.instance

        # Ensure the user is the owner of the pharmacy they are trying to edit
        if pharmacy.created_by != user:
            raise serializers.ValidationError("You do not have permission to edit this pharmacy.")
        return attrs




class PharmacyUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = PharmacyUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'pharmacy',
            'password',
            'is_superuser',
        ]
        read_only_fields = ['id', 'is_superuser']

    def validate(self, attrs):
        # Validate pharmacy assignment based on role
        role = attrs.get('role')
        pharmacy = attrs.get('pharmacy')

        if role in [PharmacyUser.ROLE_ADMIN, PharmacyUser.ROLE_PHARMACIST] and not pharmacy:
            raise serializers.ValidationError("Admins and Pharmacists must be associated with a pharmacy.")
        if role == PharmacyUser.ROLE_MAINTAINER and pharmacy:
            raise serializers.ValidationError("Maintainers cannot be associated with a pharmacy.")
        return attrs

    def create(self, validated_data):
        # Hash the password and create a new user
        password = validated_data.pop('password')
        user = PharmacyUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Update password if provided
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT login serializer to add additional user data in the response.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data.update({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        })
        return data
    

class SimpleRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=PharmacyUser.objects.all(), message="Email already exists.")]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=PharmacyUser.objects.all(), message="Username already exists.")]
    )
    password1 = serializers.CharField(write_only=True, style={'input_type': 'password'}, min_length=8)
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'}, min_length=8)

    class Meta:
        model = PharmacyUser
        fields = ['email', 'username', 'password1', 'password2']

    def validate(self, attrs):
        # Ensure passwords match
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # Extract password fields and remove them from validated data
        password = validated_data.pop('password1')
        validated_data.pop('password2')

        # Create user and set role as 'admin'
        user = PharmacyUser.objects.create(
            role=PharmacyUser.ROLE_ADMIN,
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user
