from django.db.models import Avg, Min, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from platform_app.models import Offer, OfferDetail, Order, Review
from user_auth_app.models import User

from .filters import OfferFilter
from .pagination import OfferListPagination
from .permissions import (
    HasNotWrittenReviewBefore,
    IsBusinessUser,
    IsCustomerReviewer,
    IsCustomerUser,
    IsOfferCreator,
    IsOrderReceiver,
    IsReviewer,
    IsStaff,
)
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
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.action == "list":
            user = self.request.user
            return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))
        else:
            return Order.objects.all()

    def perform_create(self, serializer):

        offer_detail_id = serializer.validated_data.get("offer_detail_id")
        offer_detail = get_object_or_404(OfferDetail, id=offer_detail_id)
        serializer.save(customer_user=self.request.user, offer_detail=offer_detail)

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]
        if self.action in ("update", "partial_update"):
            return [IsAuthenticated(), IsOrderReceiver()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsStaff()]
        return [IsAuthenticated()]


class BaseOrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    order_status = None
    response_key = None

    def get(self, request, pk):
        business_user = get_object_or_404(User, pk=pk, type=User.Type.BUSINESS)
        count = Order.objects.filter(
            business_user=business_user, status=self.order_status
        ).count()
        return Response({self.response_key: count})


class OrdersDetailView(BaseOrderCountView):
    order_status = Order.Status.IN_PROGRESS
    response_key = "order_count"


class CompletedOrdersView(BaseOrderCountView):
    order_status = Order.Status.COMPLETED
    response_key = "completed_order_count"


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


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        reviews = Review.objects.count()
        business_users = User.objects.filter(type=User.Type.BUSINESS).count()
        offers = Offer.objects.count()
        avg = Review.objects.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        average_rating = round(avg, 1) if avg is not None else 0
        return Response(
            {
                "review_count": reviews,
                "average_rating": average_rating,
                "business_profile_count": business_users,
                "offer_count": offers,
            }
        )
