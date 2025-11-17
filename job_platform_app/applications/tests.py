from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from jobs.models import Job, JobCategory
import io


from .models import Application


User = get_user_model()


class ApplicationsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="userpass", role="user")
        self.admin = User.objects.create_user(email="admin@example.com", password="adminpass", role="admin", is_staff=True)
        self.cat = JobCategory.objects.create(name="Tech", slug="tech")
        self.job = Job.objects.create(
            title="Backend Dev",
            description="desc",
            company="Acme",
            location="Remote",
            job_type="full-time",
            category=self.cat,
            salary_min="1000.00",
            salary_max="2000.00",
            posted_by=self.admin
        )

    def auth_headers(self, email, password):
        login = reverse("login")
        resp = self.client.post(login, {"email": email, "password": password}, format="json")
        return {"HTTP_AUTHORIZATION": f"Bearer {resp.data['access']}"}

    def test_user_can_apply_and_duplicate_blocked(self):
        apply_url = reverse("apply-to-job")
        headers = self.auth_headers("user@example.com", "userpass")
        
        # create a fake resume file
        resume = SimpleUploadedFile("res.pdf", b"resume-content", content_type="application/pdf")
        payload = {"job": str(self.job.id), "resume": resume, "cover_letter": "Hi"}
        resp = self.client.post(apply_url, payload, format="multipart", **headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # duplicate application attempt
        resp = self.client.post(apply_url, payload, format="multipart", **headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_apply_and_admin_can_change_status(self):
        apply_url = reverse("apply-to-job")
        headers = self.auth_headers("admin@example.com", "adminpass")
        
        resume = SimpleUploadedFile("res.pdf", b"content", content_type="application/pdf")
        payload = {"job": str(self.job.id), "resume": resume, "cover_letter": "x"}
        
        # admin trying to apply should be forbidden or raise
        resp = self.client.post(apply_url, payload, format="multipart", **headers)
        
        self.assertNotEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # create application as user
        u_headers = self.auth_headers("user@example.com", "userpass")
        resume = SimpleUploadedFile("res.pdf", b"content", content_type="application/pdf")
        resp = self.client.post(apply_url, {"job": str(self.job.id), "resume": resume, "cover_letter": "x"}, format="multipart", **u_headers)
        
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        app_id = resp.data["id"]

        # admin updates status
        detail = reverse("application-detail", kwargs={"pk": str(app_id)})
        admin_headers = self.auth_headers("admin@example.com", "adminpass")
        resp = self.client.patch(detail, {"status": "accepted"}, format="json", **admin_headers)
        # print(resp.data)
        # admin should be able to change status
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get("status"), "accepted")
