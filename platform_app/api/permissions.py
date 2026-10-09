from rest_framework.permissions import BasePermission

from user_auth_app.models import User


class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.type == User.Type.BUSINESS


class IsOfferCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("PATCH", "PUT", "DELETE"):
            return obj.user == request.user

        return True
