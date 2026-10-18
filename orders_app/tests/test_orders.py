from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from offers_app.tests.test_offers import create_offer
from orders_app.models import Order
from user_auth_app.models import User

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


class OrderTests(APITestCase):
    def setUp(self):
        self.url = reverse("orders-list")
        self.business_user = User.objects.create_user(
            username="testcustomer", password="testpassword", type="business"
        )
        self.customer_user = User.objects.create_user(
            username="testvendor", password="testpassword", type="customer"
        )
        self.unrelated_user = User.objects.create_user(
            username="unrelated", password="testpassword", type="customer"
        )

        self.token = Token.objects.create(user=self.customer_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.order = create_order(
            self.customer_user, self.business_user, offer_type="basic"
        )
        self.detail_url = reverse("orders-detail", kwargs={"pk": self.order.id})

    def authenticate_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    # GET /api/orders/

    def test_get_orders_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_orders(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_no_unrelated_orders(self):
        self.authenticate_as(self.unrelated_user)
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_orders_result_keys(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data[0].keys()), ORDER_KEYS)

    def test_get_orders_as_business_user(self):
        self.authenticate_as(self.business_user)
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.order.id)

    # POST /api/orders/

    def test_create_order_as_customer(self):
        offer = create_offer(self.business_user, title="Logo Design")
        offer_detail = offer.details.get(offer_type="premium")

        response = self.client.post(
            self.url, {"offer_detail_id": offer_detail.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), ORDER_KEYS)
        self.assertEqual(response.data["customer_user"], self.customer_user.id)
        self.assertEqual(response.data["business_user"], self.business_user.id)
        self.assertEqual(response.data["title"], offer_detail.title)
        self.assertEqual(response.data["revisions"], offer_detail.revisions)
        self.assertEqual(
            response.data["delivery_time_in_days"], offer_detail.delivery_time_in_days
        )
        self.assertEqual(float(response.data["price"]), float(offer_detail.price))
        self.assertEqual(response.data["features"], offer_detail.features)
        self.assertEqual(response.data["offer_type"], "premium")
        self.assertEqual(response.data["status"], "in_progress")

    def test_create_order_unauthenticated(self):
        offer_detail = create_offer(self.business_user).details.first()
        self.client.credentials()
        response = self.client.post(
            self.url, {"offer_detail_id": offer_detail.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_as_business_is_forbidden(self):
        offer_detail = create_offer(self.business_user).details.first()
        self.authenticate_as(self.business_user)
        response = self.client.post(
            self.url, {"offer_detail_id": offer_detail.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_missing_offer_detail_id(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_offer_detail_id(self):
        response = self.client.post(self.url, {"offer_detail_id": "abc"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_offer_detail_not_found(self):
        response = self.client.post(self.url, {"offer_detail_id": 9999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # PATCH /api/orders/{id}/

    def test_patch_order_status_as_business_user(self):
        self.authenticate_as(self.business_user)
        response = self.client.patch(
            self.detail_url, {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), ORDER_KEYS)
        self.assertEqual(response.data["status"], "completed")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "completed")

    def test_patch_order_unauthenticated(self):
        self.client.credentials()
        response = self.client.patch(
            self.detail_url, {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_order_as_customer_is_forbidden(self):
        response = self.client.patch(
            self.detail_url, {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_of_other_business_user_is_forbidden(self):
        other_business = User.objects.create_user(
            username="otherbusiness", password="testpassword", type="business"
        )
        self.authenticate_as(other_business)
        response = self.client.patch(
            self.detail_url, {"status": "completed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_invalid_status(self):
        self.authenticate_as(self.business_user)
        response = self.client.patch(self.detail_url, {"status": "done"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_order_with_forbidden_field(self):
        self.authenticate_as(self.business_user)
        response = self.client.patch(
            self.detail_url, {"status": "completed", "price": 1}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_patch_order_not_found(self):
        self.authenticate_as(self.business_user)
        url = reverse("orders-detail", kwargs={"pk": 9999})
        response = self.client.patch(url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # DELETE /api/orders/{id}/

    def test_delete_order_as_staff(self):
        admin = User.objects.create_user(
            username="admin", password="testpassword", is_staff=True
        )
        self.authenticate_as(admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_delete_order_unauthenticated(self):
        self.client.credentials()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_as_non_staff_is_forbidden(self):
        self.authenticate_as(self.business_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())

    def test_delete_order_not_found(self):
        admin = User.objects.create_user(
            username="admin", password="testpassword", is_staff=True
        )
        self.authenticate_as(admin)
        url = reverse("orders-detail", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def create_counted_orders(self):
        create_order(self.customer_user, self.business_user, offer_type="standard")
        completed = create_order(
            self.customer_user, self.business_user, offer_type="premium"
        )
        completed.status = Order.Status.COMPLETED
        completed.save()

    def test_get_order_count(self):
        self.create_counted_orders()
        url = reverse("order-count", kwargs={"pk": self.business_user.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"order_count": 2})

    def test_get_completed_order_count(self):
        self.create_counted_orders()
        url = reverse("completed-order-count", kwargs={"pk": self.business_user.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"completed_order_count": 1})

    def test_get_order_count_unauthenticated(self):
        self.client.credentials()
        for name in ("order-count", "completed-order-count"):
            url = reverse(name, kwargs={"pk": self.business_user.id})
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_order_count_business_user_not_found(self):
        for name in ("order-count", "completed-order-count"):
            url = reverse(name, kwargs={"pk": 9999})
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_count_for_customer_user_not_found(self):
        for name in ("order-count", "completed-order-count"):
            url = reverse(name, kwargs={"pk": self.customer_user.id})
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
