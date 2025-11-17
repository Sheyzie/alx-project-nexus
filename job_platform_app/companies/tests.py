from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from .models import Company

User = get_user_model()


class CompaniesAPITest(APITestCase):
    def setUp(self):
        self.list_url = reverse("company-list")  # /api/companies/
        self.user = User.objects.create_user(email="user@example.com", password="userpass", role="user")
        self.admin = User.objects.create_user(email="admin@example.com", password="adminpass", role="admin", is_staff=True)

    def get_auth_headers(self, email, password):
        login = reverse("login")

        resp = self.client.post(login, {"email": email, "password": password}, format="json")
        token = resp.data["access"]
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_public_company_list_and_retrieve(self):
        # create sample company as admin via the ORM so it exists
        company = Company.objects.create(owner=self.admin, name="Acme", description="Test")
        
        # public GET list
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        # detail view
        detail = reverse("company-detail", kwargs={"pk": str(company.id)})
        resp = self.client.get(detail)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Acme")

    def test_only_admin_can_create_company(self):
        payload = {"name": "NewCo", "description": "Desc"}
        
        # as normal user
        headers = self.get_auth_headers("user@example.com", "userpass")
        resp = self.client.post(self.list_url, payload, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # as admin
        headers = self.get_auth_headers("admin@example.com", "adminpass")
        resp = self.client.post(self.list_url, payload, format="json", **headers)
        self.assertIn(resp.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))

    def test_admin_can_update_and_delete(self):
        company = Company.objects.create(owner=self.admin, name="DeleteMe", description="x")
        detail = reverse("company-detail", kwargs={"pk": str(company.id)})

        # as user -> cannot update
        headers = self.get_auth_headers("user@example.com", "userpass")
        resp = self.client.patch(detail, {"name": "X"}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # as admin -> can update
        headers = self.get_auth_headers("admin@example.com", "adminpass")
        resp = self.client.patch(detail, {"name": "X"}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # delete as admin
        resp = self.client.delete(detail, **headers)
        self.assertIn(resp.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))
