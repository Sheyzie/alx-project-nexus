from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from locations.models import Country, State, City
from users.models import User


class LocationsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="userpass", role="user")
        self.admin = User.objects.create_user(email="admin@example.com", password="adminpass", role="admin", is_staff=True)

    def auth_headers(self, email, password):
        login = reverse("login")
        resp = self.client.post(login, {"email": email, "password": password}, format="json")
        return {"HTTP_AUTHORIZATION": f"Bearer {resp.data['access']}"}

    def test_admin_can_create_country_state_city(self):
        c_url = reverse("country-list")
        headers = self.auth_headers("admin@example.com", "adminpass")
        
        resp = self.client.post(c_url, {"name": "Narnia", "iso_code": "NA"}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        country_id = resp.data["id"]

        s_url = reverse("state-list")
        resp = self.client.post(s_url, {"name": "West", "country": country_id}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        state_id = resp.data["id"]

        city_url = reverse("city-list")
        resp = self.client.post(city_url, {"name": "Cair Paravel", "state": state_id}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_non_admin_cannot_create_location(self):
        c_url = reverse("country-list")
        headers = self.auth_headers("user@example.com", "userpass")
        resp = self.client.post(c_url, {"name": "Nowhere"}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
