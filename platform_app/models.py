from django.core.validators import MaxValueValidator, MinValueValidator
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
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In_progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="customer_orders"
    )
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="business_orders"
    )

    title = models.CharField(max_length=255)
    revisions = models.IntegerField(default=0, validators=[MinValueValidator(-1)])
    delivery_time_in_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=10, choices=OfferDetail.Type.choices)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.IN_PROGRESS
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Review(models.Model):
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="customer_reviews"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="reviews", null=True, blank=True
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business_user", "reviewer"], name="unique_review_per_user"
            ),
            models.CheckConstraint(
                condition=~models.Q(business_user=models.F("reviewer")),
                name="prevent_self_review",
            ),
        ]
