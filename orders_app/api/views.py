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
    """CRUD endpoints for orders."""

    serializer_class = OrderSerializer

    def get_queryset(self):
        """Return only the user's own orders for list, otherwise all orders."""
        if self.action == "list":
            user = self.request.user
            return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))
        else:
            return Order.objects.all()

    def perform_create(self, serializer):
        """Look up the offer detail and save the order for the requesting customer.

        Returns 404 if the offer detail does not exist.
        """

        offer_detail_id = serializer.validated_data.get("offer_detail_id")
        offer_detail = get_object_or_404(OfferDetail, id=offer_detail_id)
        serializer.save(customer_user=self.request.user, offer_detail=offer_detail)

    def get_permissions(self):
        """Return the permissions depending on the current action.

        create: customers only, update: receiving business user only,
        destroy: staff only, otherwise: authenticated users.
        """
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
    """Base view counting the orders of a business user with a given status.

    Subclasses must set order_status and response_key.
    """

    permission_classes = [IsAuthenticated]
    order_status = None
    response_key = None

    def get(self, request, pk):
        """Return the number of orders with order_status for the business user pk.

        Returns 404 if no business user with this id exists.
        """
        business_user = get_object_or_404(User, pk=pk, type=User.Type.BUSINESS)
        count = Order.objects.filter(
            business_user=business_user, status=self.order_status
        ).count()
        return Response({self.response_key: count})


class OrdersDetailView(BaseOrderCountView):
    """Return the number of in progress orders of a business user."""

    order_status = Order.Status.IN_PROGRESS
    response_key = "order_count"


class CompletedOrdersView(BaseOrderCountView):
    """Return the number of completed orders of a business user."""

    order_status = Order.Status.COMPLETED
    response_key = "completed_order_count"
