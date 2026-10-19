from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review

from .permissions import IsCustomerReviewer, IsReviewer
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for reviews with filtering and ordering."""

    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    filterset_fields = ["business_user_id", "reviewer_id"]

    ordering_fields = ["updated_at", "rating"]

    def perform_create(self, serializer):
        """Save the new review with the requesting user as reviewer.

        Runs after validation, so invalid data returns 400 before
        a second review for the same business user returns 403.
        """
        already_reviewed = Review.objects.filter(
            reviewer=self.request.user,
            business_user=serializer.validated_data["business_user"],
        ).exists()
        if already_reviewed:
            raise PermissionDenied("You have already reviewed this business user.")
        serializer.save(reviewer=self.request.user)

    def get_permissions(self):
        """Return the permissions depending on the current action.

        create: customers only, update/delete: review author only,
        otherwise: authenticated users.
        """
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerReviewer()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsReviewer()]
        return [IsAuthenticated()]
