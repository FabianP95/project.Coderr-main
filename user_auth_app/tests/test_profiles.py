from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

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
