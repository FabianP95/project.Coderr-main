from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from platform_app.models import Offer, OfferDetail
from user_auth_app.models import User

OFFER_LIST_KEYS = {
    "id",
    "user",
    "title",
    "image",
    "description",
    "created_at",
    "updated_at",
    "details",
    "min_price",
    "min_delivery_time",
    "user_details",
}

OFFER_RETRIEVE_KEYS = OFFER_LIST_KEYS - {"user_details"}

OFFER_WRITE_KEYS = {"id", "title", "image", "description", "details"}

OFFER_DETAIL_KEYS = {
    "id",
    "title",
    "revisions",
    "delivery_time_in_days",
    "price",
    "features",
    "offer_type",
}


def create_offer(user, title="Website Design", prices=(100, 200, 500), days=(7, 5, 3)):

    offer = Offer.objects.create(
        user=user, title=title, description="Professional website design"
    )
    for offer_type, price, delivery in zip(OfferDetail.Type.values, prices, days):
        OfferDetail.objects.create(
            offer=offer,
            title=f"{offer_type} design",
            revisions=2,
            delivery_time_in_days=delivery,
            price=price,
            features=["Logo Design"],
            offer_type=offer_type,
        )
    return offer


def offer_payload():

    return {
        "title": "Grafikdesign-Paket",
        "image": None,
        "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
        "details": [
            {
                "title": "Basic Design",
                "revisions": 2,
                "delivery_time_in_days": 5,
                "price": 100,
                "features": ["Logo Design", "Visitenkarte"],
                "offer_type": "basic",
            },
            {
                "title": "Standard Design",
                "revisions": 5,
                "delivery_time_in_days": 7,
                "price": 200,
                "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
                "offer_type": "standard",
            },
            {
                "title": "Premium Design",
                "revisions": 10,
                "delivery_time_in_days": 10,
                "price": 500,
                "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
                "offer_type": "premium",
            },
        ],
    }


class OfferTests(APITestCase):
    def setUp(self):
        self.url = reverse("offers-list")
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", type="business"
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.offer = create_offer(self.user)
        self.detail_url = reverse("offers-detail", kwargs={"pk": self.offer.id})

    def authenticate_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    # GET /api/offers/

    def test_get_offers_unauthenticated_is_allowed(self):
        self.client.credentials()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_offers_is_paginated(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()), {"count", "next", "previous", "results"}
        )
        self.assertEqual(response.data["count"], 1)

    def test_get_offers_result_keys(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = response.data["results"][0]
        self.assertEqual(set(result.keys()), OFFER_LIST_KEYS)
        self.assertEqual(
            set(result["user_details"].keys()),
            {"first_name", "last_name", "username"},
        )

    def test_get_offers_min_values_and_detail_links(self):
        response = self.client.get(self.url, format="json")
        result = response.data["results"][0]

        self.assertEqual(float(result["min_price"]), 100)
        self.assertEqual(result["min_delivery_time"], 3)
        self.assertEqual(len(result["details"]), 3)
        for detail in result["details"]:
            self.assertEqual(set(detail.keys()), {"id", "url"})
            self.assertIn(f"/offerdetails/{detail['id']}/", detail["url"])

    def test_filter_by_creator_id(self):
        other = User.objects.create_user(
            username="other", password="otherpassword", type="business"
        )
        create_offer(other, title="Other offer")

        response = self.client.get(self.url, {"creator_id": other.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["user"], other.id)

    def test_filter_by_min_price(self):
        create_offer(self.user, title="Expensive", prices=(1000, 2000, 3000))

        response = self.client.get(self.url, {"min_price": 500})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Expensive")

    def test_filter_by_max_delivery_time(self):
        create_offer(self.user, title="Slow", days=(30, 20, 10))

        response = self.client.get(self.url, {"max_delivery_time": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Website Design")

    def test_search_in_title_and_description(self):
        create_offer(self.user, title="Logo Paket")

        response = self.client.get(self.url, {"search": "logo"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Logo Paket")

    def test_ordering_by_min_price(self):
        create_offer(self.user, title="Cheap", prices=(10, 20, 30))

        response = self.client.get(self.url, {"ordering": "min_price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [offer["title"] for offer in response.data["results"]]
        self.assertEqual(titles, ["Cheap", "Website Design"])

    def test_page_size(self):
        create_offer(self.user, title="Second")
        create_offer(self.user, title="Third")

        response = self.client.get(self.url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])

    def test_invalid_query_param_for_price(self):
        response = self.client.get(self.url, {"min_price": "abc"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_query_param_for_creator_id(self):
        response = self.client.get(self.url, {"creator_id": "abc"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_query_param_for_max_delivery_time(self):
        response = self.client.get(self.url, {"max_delivery_time": "abc"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # POST /api/offers/

    def test_create_offer_as_business_user(self):
        response = self.client.post(self.url, offer_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(set(response.data.keys()), OFFER_WRITE_KEYS)
        self.assertEqual(len(response.data["details"]), 3)
        for detail in response.data["details"]:
            self.assertEqual(set(detail.keys()), OFFER_DETAIL_KEYS)

        offer = Offer.objects.get(id=response.data["id"])
        self.assertEqual(offer.user, self.user)
        self.assertEqual(offer.details.count(), 3)

    def test_create_offer_unauthenticated(self):
        self.client.credentials()
        response = self.client.post(self.url, offer_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_as_customer_is_forbidden(self):
        customer = User.objects.create_user(
            username="customer", password="customerpassword", type="customer"
        )
        self.authenticate_as(customer)

        response = self.client.post(self.url, offer_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Offer.objects.filter(user=customer).exists())

    def test_create_offer_with_less_than_three_details(self):
        data = offer_payload()
        data["details"] = data["details"][:2]

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("details", response.data)

    def test_create_offer_with_duplicate_offer_type(self):
        data = offer_payload()
        data["details"][2]["offer_type"] = "basic"

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_missing_title(self):
        data = offer_payload()
        del data["title"]

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    # GET /api/offers/{id}/

    def test_get_single_offer(self):
        response = self.client.get(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), OFFER_RETRIEVE_KEYS)
        self.assertEqual(float(response.data["min_price"]), 100)
        self.assertEqual(response.data["min_delivery_time"], 3)

    def test_get_single_offer_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_single_offer_not_found(self):
        url = reverse("offers-detail", kwargs={"pk": 9999})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # PATCH /api/offers/{id}/

    def test_patch_offer_as_owner(self):
        data = {
            "title": "Updated Website Design",
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": ["Logo Design", "Flyer"],
                    "offer_type": "basic",
                }
            ],
        }
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), OFFER_WRITE_KEYS)
        self.assertEqual(len(response.data["details"]), 3)

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Updated Website Design")
        basic = self.offer.details.get(offer_type="basic")
        self.assertEqual(basic.title, "Basic Design Updated")
        self.assertEqual(basic.price, 120)
        standard = self.offer.details.get(offer_type="standard")
        self.assertEqual(standard.price, 200)

    def test_patch_offer_unauthenticated(self):
        self.client.credentials()
        response = self.client.patch(self.detail_url, {"title": "x"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_offer_of_other_user_is_forbidden(self):
        other = User.objects.create_user(
            username="other", password="otherpassword", type="business"
        )
        self.authenticate_as(other)

        response = self.client.patch(self.detail_url, {"title": "Evil"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.offer.refresh_from_db()
        self.assertNotEqual(self.offer.title, "Evil")

    def test_patch_offer_not_found(self):
        url = reverse("offers-detail", kwargs={"pk": 9999})
        response = self.client.patch(url, {"title": "x"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # DELETE /api/offers/{id}/

    def test_delete_offer_as_owner(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())
        self.assertFalse(OfferDetail.objects.filter(offer_id=self.offer.id).exists())

    def test_delete_offer_unauthenticated(self):
        self.client.credentials()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_offer_of_other_user_is_forbidden(self):
        other = User.objects.create_user(
            username="other", password="otherpassword", type="business"
        )
        self.authenticate_as(other)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_offer_not_found(self):
        url = reverse("offers-detail", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferDetailTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", type="customer"
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        business_user = User.objects.create_user(
            username="business", password="businesspassword", type="business"
        )
        self.offer = create_offer(business_user)
        self.offer_detail = self.offer.details.get(offer_type="basic")
        self.url = reverse("offer-detail", kwargs={"pk": self.offer_detail.id})

    def test_get_offer_detail(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), OFFER_DETAIL_KEYS)

    def test_get_offer_detail_values(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["id"], self.offer_detail.id)
        self.assertEqual(response.data["offer_type"], "basic")
        self.assertEqual(response.data["revisions"], 2)
        self.assertEqual(response.data["delivery_time_in_days"], 7)
        self.assertEqual(float(response.data["price"]), 100)
        self.assertEqual(response.data["features"], ["Logo Design"])

    def test_get_offer_detail_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offer_detail_not_found(self):
        url = reverse("offer-detail", kwargs={"pk": 9999})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offer_detail_is_read_only(self):
        response = self.client.patch(self.url, {"price": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.offer_detail.refresh_from_db()
        self.assertEqual(self.offer_detail.price, 100)
