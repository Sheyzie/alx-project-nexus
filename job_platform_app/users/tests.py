from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Profile


User = get_user_model()


class UsersAPITest(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")         
        self.login_url = reverse("login")              
        self.refresh_url = reverse("token_refresh")    
        self.profile_url = reverse("profile")            

        # create an admin user
        self.admin = User.objects.create_user(email="admin@example.com", password="pass1234", role="admin", is_staff=True)
        
        # create a normal user
        self.user = User.objects.create_user(email="user@example.com", password="userpass", role="user")

    def get_token_for(self, email, password):
        resp = self.client.post(self.login_url, {"email": email, "password": password}, format="json")
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        return resp.data["access"], resp.data["refresh"]

    def test_register_and_profile_created(self):
        payload = {"email": "new@example.com", "password": "newpass123"}
        resp = self.client.post(self.register_url, payload, format="json")
        
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="new@example.com")
        
        # profile auto-created
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)

    def test_login_and_refresh(self):
        access, refresh = self.get_token_for("user@example.com", "userpass")
        self.assertIsNotNone(access)
        
        # refresh
        refresh_resp = self.client.post(self.refresh_url, {"refresh": refresh}, format="json")

        self.assertEqual(refresh_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_resp.data)

    def test_get_and_update_profile(self):
        access, _ = self.get_token_for("user@example.com", "userpass")
        # self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # GET profile
        resp = self.client.get(self.profile_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("user", resp.data)

        # PATCH profile
        resp = self.client.patch(self.profile_url, {"fullname": "Test User", "headline": "Hello"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["fullname"], "Test User")

