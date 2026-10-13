from django.db.models import Q
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import OfferDetail
from orders_app.models import Order
from user_auth_app.models import User

from .permissions import IsCustomerUser, IsOrderReceiver, IsStaff
from .serializers import OrderSerializer


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
