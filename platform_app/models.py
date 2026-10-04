from django.core.validators import MinValueValidator
from django.db import models

from user_auth_app.models import User


class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255, blank=False)
    image = models.FileField(upload_to="offer_pictures", blank=True, null=True)
    description = models.TextField(max_length=500, blank=False, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OfferDetail(models.Model):
    class Type(models.TextChoices):
        BASIC = "basic", "Basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    title = models.CharField(max_length=255, blank=False)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    revisions = models.IntegerField(default=0, validators=[MinValueValidator(-1)])
    delivery_time_in_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=10, choices=Type.choices)

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"], name="unique_offer_type_per_offer"
            )
        ]


class Order(models.Model):
    pass


class Review(models.Model):
    pass
