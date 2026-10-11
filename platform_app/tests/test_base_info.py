from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from platform_app.models import Review
from user_auth_app.models import User

from .test_offers import create_offer


class BaseInfoTests(APITestCase):
    def setUp(self):
        self.url = reverse("base-info")
        self.business_user = User.objects.create_user(
            username="testbusiness", password="testpassword", type="business"
        )
        self.second_business_user = User.objects.create_user(
            username="testbusiness2", password="testpassword", type="business"
        )
        self.customer_user = User.objects.create_user(
            username="testcustomer", password="testpassword", type="customer"
        )
        self.second_customer_user = User.objects.create_user(
            username="testcustomer2", password="testpassword", type="customer"
        )

    def create_base_info_data(self):
        create_offer(self.business_user)
        create_offer(self.business_user, title="Logo Design")
        create_offer(self.second_business_user, title="App Development")
        Review.objects.create(
            business_user=self.business_user, reviewer=self.customer_user, rating=5
        )
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.second_customer_user,
            rating=4,
        )
        Review.objects.create(
            business_user=self.second_business_user,
            reviewer=self.customer_user,
            rating=4,
        )

    def test_get_base_info(self):
        self.create_base_info_data()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {"review_count", "average_rating", "business_profile_count", "offer_count"},
        )
        self.assertEqual(response.data["review_count"], 3)
        self.assertEqual(response.data["business_profile_count"], 2)
        self.assertEqual(response.data["offer_count"], 3)

    def test_get_base_info_average_rating_rounded_to_one_decimal(self):
        self.create_base_info_data()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["average_rating"], 4.3)

    def test_get_base_info_without_data(self):
        User.objects.all().delete()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "review_count": 0,
                "average_rating": 0,
                "business_profile_count": 0,
                "offer_count": 0,
            },
        )

    def test_get_base_info_counts_only_business_users(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["business_profile_count"], 2)

    def test_get_base_info_unauthenticated_allowed(self):
        self.client.credentials()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_write_methods_not_allowed(self):
        for method in ("post", "put", "patch", "delete"):
            response = getattr(self.client, method)(self.url, {}, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
            )
