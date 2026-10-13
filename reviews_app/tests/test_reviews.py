from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from reviews_app.models import Review
from user_auth_app.models import User

REVIEW_KEYS = {
    "id",
    "business_user",
    "reviewer",
    "rating",
    "description",
    "created_at",
    "updated_at",
}


class ReviewTests(APITestCase):
    def setUp(self):
        self.url = reverse("reviews-list")
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

        self.token = Token.objects.create(user=self.customer_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description="Good work.",
        )
        self.detail_url = reverse("reviews-detail", kwargs={"pk": self.review.id})

    def authenticate_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    def create_additional_reviews(self):
        self.second_review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.second_customer_user,
            rating=2,
            description="Okay.",
        )
        self.third_review = Review.objects.create(
            business_user=self.second_business_user,
            reviewer=self.customer_user,
            rating=5,
            description="Excellent.",
        )

    # GET /api/reviews/

    def test_get_reviews(self):
        self.create_additional_reviews()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_reviews_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_reviews_result_keys(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data[0].keys()), REVIEW_KEYS)

    def test_get_reviews_filter_by_business_user_id(self):
        self.create_additional_reviews()
        response = self.client.get(
            self.url, {"business_user_id": self.business_user.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for review in response.data:
            self.assertEqual(review["business_user"], self.business_user.id)

    def test_get_reviews_filter_by_reviewer_id(self):
        self.create_additional_reviews()
        response = self.client.get(
            self.url, {"reviewer_id": self.customer_user.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for review in response.data:
            self.assertEqual(review["reviewer"], self.customer_user.id)

    def test_get_reviews_ordering_by_rating(self):
        self.create_additional_reviews()
        response = self.client.get(self.url, {"ordering": "rating"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [review["rating"] for review in response.data]
        self.assertEqual(ratings, sorted(ratings))

    def test_get_reviews_ordering_by_rating_descending(self):
        self.create_additional_reviews()
        response = self.client.get(self.url, {"ordering": "-rating"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [review["rating"] for review in response.data]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_get_reviews_ordering_by_updated_at(self):
        self.create_additional_reviews()
        response = self.client.get(self.url, {"ordering": "updated_at"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [review["updated_at"] for review in response.data]
        self.assertEqual(dates, sorted(dates))

    # POST /api/reviews/

    def test_create_review_as_customer(self):
        data = {
            "business_user": self.second_business_user.id,
            "rating": 5,
            "description": "Great collaboration.",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), REVIEW_KEYS)
        self.assertEqual(response.data["business_user"], self.second_business_user.id)
        self.assertEqual(response.data["reviewer"], self.customer_user.id)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["description"], "Great collaboration.")

    def test_create_review_unauthenticated(self):
        self.client.credentials()
        data = {"business_user": self.second_business_user.id, "rating": 5}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_as_business_is_unauthorized(self):
        self.authenticate_as(self.second_business_user)
        data = {"business_user": self.business_user.id, "rating": 5}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_second_review_for_same_business_user_is_forbidden(self):
        data = {"business_user": self.business_user.id, "rating": 1}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            Review.objects.filter(
                business_user=self.business_user, reviewer=self.customer_user
            ).count(),
            1,
        )

    def test_create_review_missing_rating(self):
        data = {"business_user": self.second_business_user.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_missing_description(self):
        data = {"business_user": 2, "rating": 4}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_missing_business_user(self):
        response = self.client.post(self.url, {"rating": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_rating_out_of_range(self):
        for rating in (0, 6):
            data = {"business_user": self.second_business_user.id, "rating": rating}
            response = self.client.post(self.url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_business_user_not_found(self):
        data = {"business_user": 9999, "rating": 5}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_for_customer_user_is_invalid(self):
        data = {"business_user": self.second_customer_user.id, "rating": 5}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # PATCH /api/reviews/{id}/

    def test_patch_review_as_reviewer(self):
        data = {"rating": 5, "description": "Even better than expected."}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), REVIEW_KEYS)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["description"], "Even better than expected.")
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)

    def test_patch_review_unauthenticated(self):
        self.client.credentials()
        response = self.client.patch(self.detail_url, {"rating": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_review_of_other_user_is_forbidden(self):
        self.authenticate_as(self.second_customer_user)
        response = self.client.patch(self.detail_url, {"rating": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)

    def test_patch_review_with_forbidden_field(self):
        data = {"rating": 5, "business_user": self.second_business_user.id}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.review.refresh_from_db()
        self.assertEqual(self.review.business_user, self.business_user)
        self.assertEqual(self.review.rating, 4)

    def test_patch_review_invalid_rating(self):
        response = self.client.patch(self.detail_url, {"rating": 10}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_review_not_found(self):
        url = reverse("reviews-detail", kwargs={"pk": 9999})
        response = self.client.patch(url, {"rating": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # DELETE /api/reviews/{id}/

    def test_delete_review_as_reviewer(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_unauthenticated(self):
        self.client.credentials()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_of_other_user_is_forbidden(self):
        self.authenticate_as(self.second_customer_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_not_found(self):
        url = reverse("reviews-detail", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
