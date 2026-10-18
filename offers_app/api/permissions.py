from rest_framework.permissions import BasePermission

from user_auth_app.models import User


class IsBusinessUser(BasePermission):
    """Allow access only to users of type business."""

    def has_permission(self, request, view):
        """Return True if the requesting user is a business user."""
        return request.user.type == User.Type.BUSINESS


class IsOfferCreator(BasePermission):
    """Allow modifying or deleting an offer only to its creator."""

    def has_object_permission(self, request, view, obj):
        """Check ownership for write methods, allow all other methods."""
        if request.method in ("PATCH", "PUT", "DELETE"):
            return obj.user == request.user

        return True
