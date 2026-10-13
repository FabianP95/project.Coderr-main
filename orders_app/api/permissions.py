from rest_framework.permissions import BasePermission

from user_auth_app.models import User


class IsCustomerUser(BasePermission):
    """Allow access only to users of type customer."""

    def has_permission(self, request, view):
        """Return True if the requesting user is a customer user."""
        return request.user.type == User.Type.CUSTOMER


class IsStaff(BasePermission):
    """Allow access only to staff users."""

    def has_permission(self, request, view):
        """Return True if the requesting user is a staff member."""
        return request.user.is_staff


class IsOrderReceiver(BasePermission):
    """Allow access only to the business user who received the order."""

    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user is the business user of the order."""
        return obj.business_user == request.user
