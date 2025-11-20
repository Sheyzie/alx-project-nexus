from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from jobs.models import Job, JobCategory
from graphene_django.utils.testing import GraphQLTestCase
from job_platform.schema import schema
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


class TestGraphQLAPI(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "/graphql/"

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

    def get_token_for(self, email, password):
        mutation = '''
            mutation getAuth ($email: String!, $password: String!){
                tokenAuth(email: $email, password: $password) {
                    token
                }
            }
        '''

        resp = self.query(
            query=mutation,
            variables={
                "email": email,
                "password": password
            }
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()  
        token = data['data']['tokenAuth']['token']    
        return token
    
    def test_get_applications(self):
        token = self.get_token_for("user@example.com", "userpass")

        headers = {"Authorization": f"JWT {token}"}
        
        resume = SimpleUploadedFile("res.pdf", b"resume-content", content_type="application/pdf")
        payload = {"resume": resume, "cover_letter": "Hi"}
        
        application = Application.objects.create(applicant=self.user, job=self.job, **payload)

        query = '''
            query getApplications {
                applications {
                    id
                    job {
                        title
                        company
                    }
                    applicant {
                        id
                        email
                    }
                    resume
                    coverLetter
                    status
                    createdAt
                }
            }
        '''

        resp = self.query(
            query,
            headers=headers
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, 'resume')

    def test_get_application(self):
        token = self.get_token_for("user@example.com", "userpass")

        headers = {"Authorization": f"JWT {token}"}
        
        resume = SimpleUploadedFile("res.pdf", b"resume-content", content_type="application/pdf")
        payload = {"resume": resume, "cover_letter": "Hi"}
        
        application = Application.objects.create(applicant=self.user, job=self.job, **payload)

        query = '''
            query getApplications ($id: UUID!) {
                application (id: $id) {
                    id
                    job {
                        title
                        company
                    }
                    applicant {
                        id
                        email
                    }
                    resume
                    coverLetter
                    status
                    createdAt
                }
            }
        '''

        resp = self.query(
            query,
            variables={"id": str(application.id)},
            headers=headers
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, 'resume')

    
    def test_create_application(self):
        # create job with user token
        token = self.get_token_for("user@example.com", "userpass")

        headers = {"Authorization": f"JWT {token}"}

        resume = SimpleUploadedFile("res.pdf", b"resume-content", content_type="application/pdf")
        # payload = {"job": str(self.job.id), "resume": resume, "cover_letter": "Hi"}

        query = '''
            mutation applyForJob($jobId: UUID!, $resume: String!, $coverLetter: String) {
                applyForJob(jobId: $jobId, resume: $resume, coverLetter: $coverLetter) {
                    application {
                        id
                        job {
                            title
                            company
                        }
                        applicant {
                            id
                            email
                        }
                        resume
                        coverLetter
                        status
                        createdAt
                    }
                }
            }
        '''

        resp = self.query(
            query=query,
            operation_name="applyForJob",
            variables={"jobId": str(self.job.id), "resume": str(resume), "coverLetter": "Hi"},
            headers=headers
        )

        self.assertContains(resp, resume)
        self.assertContains(resp, "Hi")
        self.assertContains(resp, "SUBMITTED")

        # Try to apply with admin
        token = self.get_token_for("admin@example.com", "adminpass")

        headers = {"Authorization": f"JWT {token}"}

        resume = SimpleUploadedFile("res.pdf", b"resume-content", content_type="application/pdf")

        resp = self.query(
            query=query,
            operation_name="applyForJob",
            variables={"jobId": str(self.job.id), "resume": str(resume), "coverLetter": "Hi"},
            headers=headers
        )

        self.assertContains(resp, "Unauthorised. Only a user can apply!")

    def test_update_application_status(self):
        token = self.get_token_for("admin@example.com", "adminpass")

        headers = {"Authorization": f"JWT {token}"}
        
        resume = SimpleUploadedFile("res.pdf", b"resume-content", content_type="application/pdf")
        payload = {"resume": resume, "cover_letter": "Hi"}
        
        application = Application.objects.create(applicant=self.user, job=self.job, **payload)

        query = '''
            mutation updateApplicationStatus($id: UUID!, $status: String!) {
                updateApplicationStatus(id: $id, status: $status) {
                    application {
                        id
                        resume
                        coverLetter
                        status
                        createdAt
                    }
                }
            }
        '''

        resp = self.query(
            query=query,
            operation_name="updateApplicationStatus",
            variables={"id": str(application.id), "status": "accepted"},
            headers=headers
        )

        self.assertContains(resp, "ACCEPTED")

        # try to change status as a user
        token = self.get_token_for("user@example.com", "userpass")

        headers = {"Authorization": f"JWT {token}"}

        resp = self.query(
            query=query,
            operation_name="updateApplicationStatus",
            variables={"id": str(application.id), "status": "submitted"},
            headers=headers
        )

        self.assertContains(resp, "Unauthorised. Only a admin can update!")
        
