from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from user_auth_app.models import User


class RegistrationTests(APITestCase):

    def setUp(self):
        self.url = reverse("registration")
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@mail.de"
        )

    def test_register(self):

        data = {
            "username": "user2",
            "password": "password2",
            "repeated_password": "password2",
            "email": "test@mail.com",
            "type": "customer",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            set(response.data.keys()), {"token", "username", "email", "user_id"}
        )
        new_user = User.objects.get(username="user2")
        self.assertTrue(new_user.check_password("password2"))
        self.assertNotEqual(new_user.password, "password2")
        self.assertEqual(new_user.type, "customer")

    def test_password_not_matching(self):

        data = {
            "username": "user2",
            "password": "password2",
            "repeated_password": "password",
            "email": "test@mail.com",
            "type": "customer",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("repeated_password", response.data)
        self.assertFalse(User.objects.filter(username="user2").exists())

    def test_email_already_existing(self):

        data = {
            "username": "user2",
            "password": "password2",
            "repeated_password": "password2",
            "email": "test@mail.de",
            "type": "customer",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_email_already_existing_case_insensitive(self):

        data = {
            "username": "user2",
            "password": "password2",
            "repeated_password": "password2",
            "email": "TEST@Mail.de",
            "type": "customer",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_username_already_existing(self):

        data = {
            "username": "testuser",
            "password": "password2",
            "repeated_password": "password2",
            "email": "other@mail.com",
            "type": "customer",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_missing_email(self):

        data = {
            "username": "user2",
            "password": "password2",
            "repeated_password": "password2",
            "type": "customer",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_invalid_email_format(self):

        data = {
            "username": "user2",
            "password": "password2",
            "repeated_password": "password2",
            "email": "invalid-mail.com",
            "type": "customer",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_invalid_type(self):

        data = {
            "username": "user2",
            "password": "password2",
            "repeated_password": "password2",
            "email": "test@mail.com",
            "type": "custo",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.url = reverse("login")

    def test_login(self):

        data = {
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            set(response.data.keys()), {"token", "username", "email", "user_id"}
        )

        self.assertEqual(response.data["user_id"], self.user.id)

    def test_login_returns_same_token(self):

        data = {
            "username": "testuser",
            "password": "testpassword",
        }
        first = self.client.post(self.url, data, format="json")
        second = self.client.post(self.url, data, format="json")

        # get_or_create() must reuse the existing token instead of creating a new one.
        self.assertEqual(first.data["token"], second.data["token"])

    def test_invalid_password(self):

        data = {
            "username": "testuser",
            "password": "testpassword2",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertNotIn("token", response.data)

    def test_invalid_username(self):

        data = {
            "username": "testuser2",
            "password": "testpassword",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_missing_fields(self):

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("password", response.data)


class UserProfileTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.url = reverse("profile-detail", kwargs={"pk": self.user.id})
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_profile(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "user",
                "username",
                "first_name",
                "last_name",
                "file",
                "location",
                "tel",
                "description",
                "working_hours",
                "type",
                "email",
                "created_at",
            },
        )

    def test_update_profile_via_put(self):
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Berlin",
            "tel": "987654321",
            "description": "Updated business description",
            "working_hours": "10-18",
            "email": "new_email@business.de",
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "user",
                "username",
                "first_name",
                "last_name",
                "file",
                "location",
                "tel",
                "description",
                "working_hours",
                "type",
                "email",
                "created_at",
            },
        )

    def test_update_profile_via_patch(self):
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Berlin",
            "tel": "987654321",
            "description": "Updated business description",
            "working_hours": "10-18",
            "email": "new_email@business.de",
        }
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "user",
                "username",
                "first_name",
                "last_name",
                "file",
                "location",
                "tel",
                "description",
                "working_hours",
                "type",
                "email",
                "created_at",
            },
        )

    def test_patch_changes_values_in_database(self):
        data = {"first_name": "Max", "location": "Berlin"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Max")
        self.assertEqual(self.user.location, "Berlin")

    def test_patch_cannot_change_read_only_fields(self):
        data = {"username": "hacker", "type": "business"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "testuser")
        self.assertNotEqual(self.user.type, "business")

    def test_patch_email_already_used_by_other_user(self):
        User.objects.create_user(
            username="other", password="otherpassword", email="taken@mail.de"
        )
        response = self.client.patch(
            self.url, {"email": "TAKEN@mail.de"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_empty_text_fields_are_strings_not_null(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for field in [
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
        ]:
            self.assertEqual(response.data[field], "", msg=field)

    def test_get_profile_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found(self):
        url = reverse("profile-detail", kwargs={"pk": 9999})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_of_other_user_is_allowed(self):
        other = User.objects.create_user(username="other", password="otherpassword")
        url = reverse("profile-detail", kwargs={"pk": other.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "other")

    def test_patch_profile_of_other_user_is_forbidden(self):
        other = User.objects.create_user(username="other", password="otherpassword")
        url = reverse("profile-detail", kwargs={"pk": other.id})
        response = self.client.patch(url, {"first_name": "Evil"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        other.refresh_from_db()
        self.assertNotEqual(other.first_name, "Evil")


class BusinessProfilesTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", type="business"
        )
        self.url = reverse("profiles-business")
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_all_profiles(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data[0].keys()),
            {
                "user",
                "username",
                "first_name",
                "last_name",
                "file",
                "location",
                "tel",
                "description",
                "working_hours",
                "type",
            },
        )
       

    def test_list_contains_only_business_users(self):
        User.objects.create_user(
            username="business2", password="password", type="business"
        )
        User.objects.create_user(
            username="customer1", password="password", type="customer"
        )
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        for profile in response.data:
            self.assertEqual(profile["type"], "business")

    def test_get_all_profiles_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerProfilesTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", type="customer"
        )
        self.url = reverse("profiles-customer")
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_all_profiles(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data[0].keys()),
            {
                "user",
                "username",
                "first_name",
                "last_name",
                "file",
                "uploaded_at",
                "type",
            },
        )
       

    def test_list_contains_only_customer_users(self):
        User.objects.create_user(
            username="customer2", password="password", type="customer"
        )
        User.objects.create_user(
            username="business1", password="password", type="business"
        )
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        for profile in response.data:
            self.assertEqual(profile["type"], "customer")

    def test_get_all_profiles_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
