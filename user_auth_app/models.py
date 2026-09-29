"""User profile model used for authentication and display metadata."""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Type(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    file = models.FileField(upload_to='profile_pictures', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True, default="")
    type = models.CharField(max_length=10, choices=Type.choices)
    description = models.TextField(max_length=500, blank=True, default="")
    tel = models.CharField(max_length=20, blank=True, default="")
    working_hours = models.CharField(max_length=100, blank=True, default="")
