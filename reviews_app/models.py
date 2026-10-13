from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from user_auth_app.models import User


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
    description = models.TextField(max_length=500, blank=False, default="")
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
