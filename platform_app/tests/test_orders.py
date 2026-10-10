from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from platform_app.models import Order, Offer
from user_auth_app.models import User
from .test_offers import create_offer

ORDER_KEYS = {
    "id",
    "customer_user",
    "business_user",
    "title",
    "revisions",
    "delivery_time_in_days",
    "price",
    "features",
    "offer_type",
    "status",
    "created_at",
    "updated_at",
}


def create_order(user, business_user, offer_type):

    offer = create_offer(business_user)
    offer_detail = offer.details.get(offer_type=offer_type)

    order = Order.objects.create(
        customer_user=user,
        business_user=offer.user,
        title=offer.title,
        revisions=offer_detail.revisions,
        delivery_time_in_days=offer_detail.delivery_time_in_days,
        price=offer_detail.price,
        features=offer_detail.features,
        offer_type=offer_detail.offer_type,
    )

    return order


def order_payload():
    return {"offer_detail_id": 1}


class OrderTests(APITestCase):

    def setUp(self):
        self.url = reverse("orders-list")
        self.business_user = User.objects.create_user(
            username="testcustomer", password="testpassword", type="business"
        )
        self.customer_user = User.objects.create_user(
            username="testvendor", password="testpassword", type="customer"
        )

        self.token = Token.objects.create(user=self.customer_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.order = create_order(
            self.customer_user, self.business_user, offer_type="basic"
        )
        self.detail_url = reverse("orders-detail", kwargs={"pk": self.order.id})

    def test_get_orders_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
