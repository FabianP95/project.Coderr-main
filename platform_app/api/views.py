from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from platform_app.models import Offer, OfferDetail

from .filters import OfferFilter
from .pagination import OfferListPagination
from .permissions import IsBusinessUser, IsOfferCreator
from .serializers import (
    OfferDetailSerializer,
    OfferReadsSerializer,
    OfferWriteSerializer,
    OrderSerializer,
    ReviewSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
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

        return Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        if self.action == "create":
            return [IsAuthenticated(), IsBusinessUser()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsOfferCreator()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return OfferWriteSerializer
        return OfferReadsSerializer


class OfferDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OfferDetailSerializer

    def get_queryset(self):
        offer_id = self.kwargs["pk"]
        return OfferDetail.objects.filter(offer_id=offer_id)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer


class OrdersDetailView(APIView):
    permission_classes = [IsAuthenticated]


class CompletedOrdersView(APIView):
    permission_classes = [IsAuthenticated]


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer


class BaseInfoView(APIView):
    permission_classes = [AllowAny]
