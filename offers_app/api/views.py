from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.models import Offer, OfferDetail

from .filters import OfferFilter
from .pagination import OfferListPagination
from .permissions import IsBusinessUser, IsOfferCreator
from .serializers import (
    OfferDetailSerializer,
    OfferReadsSerializer,
    OfferWriteSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for offers with filtering, search, ordering and pagination."""

    queryset = Offer.objects.all()
    pagination_class = OfferListPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = OfferFilter

    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]

    def get_queryset(self):
        """Return all offers annotated with their minimum price and delivery time."""

        return Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

    def get_permissions(self):
        """Return the permissions depending on the current action.

        list: everyone, create: business users only,
        update/delete: offer creator only, otherwise: authenticated users.
        """
        if self.action == "list":
            return [AllowAny()]
        if self.action == "create":
            return [IsAuthenticated(), IsBusinessUser()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsOfferCreator()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Save the new offer with the requesting user as creator."""
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Use the write serializer for write actions, otherwise the read serializer."""
        if self.action in ("create", "update", "partial_update", "destroy"):
            return OfferWriteSerializer
        return OfferReadsSerializer


class OfferDetailView(generics.RetrieveAPIView):
    """Return a single offer detail for authenticated users."""

    permission_classes = [IsAuthenticated]
    serializer_class = OfferDetailSerializer

    def get_queryset(self):
        """Return all offerdetails."""
        return OfferDetail.objects.all()
