from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission

from platform_app.models import Review
from user_auth_app.models import User


class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.type == User.Type.BUSINESS


class IsOfferCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("PATCH", "PUT", "DELETE"):
            return obj.user == request.user

        return True


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.type == User.Type.CUSTOMER


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class IsOrderReceiver(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user


class HasNotWrittenReviewBefore(BasePermission):
    def has_permission(self, request, view):
        return not Review.objects.filter(
            reviewer=request.user, business_user=request.data.get("business_user")
        ).exists()


class IsReviewer(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("PATCH", "PUT", "DELETE"):
            return obj.reviewer == request.user

        return True


class IsCustomerReviewer(BasePermission):
    def has_permission(self, request, view):
        if request.user.type != User.Type.CUSTOMER:
            raise NotAuthenticated("Reviewer must be a customer.")
        return True
