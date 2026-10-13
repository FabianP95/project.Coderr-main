from rest_framework.permissions import BasePermission

from reviews_app.models import Review
from user_auth_app.models import User


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
        return request.user.type == User.Type.CUSTOMER
