from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


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

