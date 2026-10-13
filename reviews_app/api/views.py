from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review

from .permissions import HasNotWrittenReviewBefore, IsCustomerReviewer, IsReviewer
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    filterset_fields = ["business_user_id", "reviewer_id"]

    ordering_fields = ["updated_at", "rating"]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "create":
            return [
                IsAuthenticated(),
                IsCustomerReviewer(),
                HasNotWrittenReviewBefore(),
            ]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsReviewer()]
        return [IsAuthenticated()]
