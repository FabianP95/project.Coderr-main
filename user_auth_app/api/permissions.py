from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProfileCreator(BasePermission):
    """Allow modifying a profile only to its owner."""

    def has_object_permission(self, request, view, obj):
        """Allow safe methods for everyone, write methods only for the owner."""
        if request.method not in SAFE_METHODS:
            return obj == request.user

        return True
