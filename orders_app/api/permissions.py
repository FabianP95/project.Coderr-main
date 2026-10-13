from rest_framework.permissions import BasePermission

from user_auth_app.models import User


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.type == User.Type.CUSTOMER


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class IsOrderReceiver(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user
