from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProfileCreator(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return obj == request.user
            
        return True
