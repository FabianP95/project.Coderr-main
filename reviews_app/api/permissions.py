from rest_framework.permissions import BasePermission

from reviews_app.models import Review
from user_auth_app.models import User


class HasNotWrittenReviewBefore(BasePermission):
    """Deny creating a second review for the same business user."""

    def has_permission(self, request, view):
        """Return True if the user has not reviewed the given business user yet."""
        return not Review.objects.filter(
            reviewer=request.user, business_user=request.data.get("business_user")
        ).exists()


class IsReviewer(BasePermission):
    """Allow modifying or deleting a review only to its author."""

    def has_object_permission(self, request, view, obj):
        """Check authorship for write methods, allow all other methods."""
        if request.method in ("PATCH", "PUT", "DELETE"):
            return obj.reviewer == request.user

        return True


class IsCustomerReviewer(BasePermission):
    """Allow access only to users of type customer."""

    def has_permission(self, request, view):
        """Return True if the requesting user is a customer user."""
        return request.user.type == User.Type.CUSTOMER
