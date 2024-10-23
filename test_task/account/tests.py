from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase


class UserCreateViewTest(APITestCase):
    def setUp(self) -> None:
        """
        Set up the test case with necessary data.
        """
        self.url = reverse("register")
        self.valid_payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
            "password2": "testpassword123",
        }
        self.invalid_payload = {
            "username": "",
            "password": "short",
            "email": "invalid-email-format",
        }

    def test_create_user_success(self) -> None:
        """
        Test user creation with valid data.
        """
        response: Response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"message": "User created."})
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_create_user_invalid_data(self) -> None:
        """
        Test user creation with invalid data.
        """
        response: Response = self.client.post(self.url, self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_authenticated(self) -> None:
        """
        Test that an authenticated user cannot create a new user.
        """
        self.client.force_authenticate(
            user=User.objects.create_user(username="existinguser", password="12345678")
        )
        response: Response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
