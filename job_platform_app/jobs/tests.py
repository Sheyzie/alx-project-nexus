from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase
from job_platform.schema import schema

from .models import Job, JobCategory

User = get_user_model()


class JobsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="userpass", role="user")
        self.admin = User.objects.create_user(email="admin@example.com", password="adminpass", role="admin", is_staff=True)

        self.cat = JobCategory.objects.create(name="Tech", slug="tech")
        
        # create a job posted by admin
        self.job = Job.objects.create(
            title="Backend Developer",
            description="Work with Django",
            company="Acme",
            location="Lagos, NG",
            full_location=None,
            job_type="full-time",
            category=self.cat,
            salary_min="50000.00",
            salary_max="150000.00",
            posted_by=self.admin
        )

    def auth_headers(self, email, password):
        login = reverse("login")
        resp = self.client.post(login, {"email": email, "password": password}, format="json")
        return {"HTTP_AUTHORIZATION": f"Bearer {resp.data['access']}"}

    def test_list_and_retrieve_jobs(self):
        list_url = reverse("job-list")
        resp = self.client.get(list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        detail = reverse("job-detail", kwargs={"pk": str(self.job.id)})
        resp = self.client.get(detail)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["title"], "Backend Developer")

    def test_only_admin_can_create_update_delete_job(self):
        list_url = reverse("job-list")
        payload = {
            "title": "Frontend Dev",
            "description": "React",
            "company": "X",
            "location": "Remote",
            "job_type": "full-time",
            "category_id": str(self.cat.id),
            "salary_min": "1000.00",
            "salary_max": "2000.00"
        }

        # user -> cannot create
        headers = self.auth_headers("user@example.com", "userpass")
        resp = self.client.post(list_url, payload, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # admin -> create
        headers = self.auth_headers("admin@example.com", "adminpass")
        resp = self.client.post(list_url, payload, format="json", **headers)
        self.assertIn(resp.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        created_job_id = resp.data["id"]

        # admin update
        detail = reverse("job-detail", kwargs={"pk": created_job_id})
        resp = self.client.patch(detail, {"title": "Updated"}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # admin delete
        resp = self.client.delete(detail, **headers)
        self.assertIn(resp.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))

    def test_search_and_filters(self):
        list_url = reverse("job-list")
        resp = self.client.get(list_url + "?search=Backend")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.get(list_url + f"?category={str(self.cat.id)}&job_type=full-time")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class TestGraphQLAPI(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="userpass", role="user")
        self.admin = User.objects.create_user(email="admin@example.com", password="adminpass", role="admin", is_staff=True)

        self.cat = JobCategory.objects.create(name="Tech", slug="tech")
        
        # create a job posted by admin
        self.job = Job.objects.create(
            title="Backend Developer",
            description="Work with Django",
            company="Acme",
            location="Lagos, NG",
            full_location=None,
            job_type="full-time",
            category=self.cat,
            salary_min="50000.00",
            salary_max="150000.00",
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
    
    def test_get_jobs(self):
        token = self.get_token_for("user@example.com", "userpass")

        headers = {"Authorization": f"JWT {token}"}

        query = '''
            query getJobs {
                jobs {
                    id
                    title
                    description 
                    company
                    location
                    category {
                        name
                        slug
                    }
                    postedBy {
                        id
                        email
                    }
                }
            }
        '''

        resp = self.query(
            query,
            headers=headers    
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, 'postedBy')

    def test_get_job(self):
        token = self.get_token_for("user@example.com", "userpass")

        headers = {"Authorization": f"JWT {token}"}

        query = '''
            query getJob ($id: UUID!) {
                job (id: $id) {
                    id
                    title
                    description 
                    company
                    location
                    category {
                        name
                        slug
                    }
                    postedBy {
                        id
                        email
                    }
                }
            }
        '''

        resp = self.query(
            query=query,
            variables={"id": str(self.job.id)},
            headers=headers
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, 'postedBy')

    def test_create_job(self):
        # create job with admin token
        token = self.get_token_for("admin@example.com", "adminpass")

        headers = {"Authorization": f"JWT {token}"}

        data = {
            'title': "New Backend Developer",
            'description': "Work with Django DRF", 
            'company': "Ikeja",
            'jobType': "full-time",
            'location': "Lagos, NG",
            "latitude": 6.5244,
            "longitude": 3.3792,
            "salaryMin": 1500.0,
            "salaryMax": 3000.0,
            'categoryId': str(self.cat.id)
        }

        query = '''
            mutation createJob($input: JobInput!) {
                createJob(input: $input) {
                    job {
                        id
                        title
                        company
                        jobType
                        postedBy {
                            id
                            email
                        }
                    }
                }
            }
        '''

        resp = self.query(
            query=query,
            operation_name="createJob",
            variables={"input": data},
            headers=headers
        )

        self.assertContains(resp, data['title'])
        self.assertContains(resp, data['company'])

    def test_unauthorised_create_job(self):        
        # test unathorised user
        token = self.get_token_for("user@example.com", "userpass")

        headers = {"Authorization": f"JWT {token}"}

        data = {
            'title': "New Backend Developer",
            'description': "Work with Django DRF", 
            'company': "Ikeja",
            'jobType': "full-time",
            'location': "Lagos, NG",
            "latitude": 6.5244,
            "longitude": 3.3792,
            "salaryMin": 1500.0,
            "salaryMax": 3000.0,
            'categoryId': str(self.cat.id)
        }

        query = '''
            mutation createJob($input: JobInput!) {
                createJob(input: $input) {
                    job {
                        id
                        title
                        company
                        jobType
                        postedBy {
                            id
                            email
                        }
                    }
                }
            }
        '''

        resp = self.query(
            query=query,
            operation_name="createJob",
            variables={"input": data},
            headers=headers
        )

        self.assertContains(resp, 'Unauthorised. User not an Admin!')

    def test_update_job(self):
        # update job with admin token
        token = self.get_token_for("admin@example.com", "adminpass")

        headers = {"Authorization": f"JWT {token}"}

        data = {
            'title': "New Backend Developer Updated",
            'description': "Work with Django DRF", 
            'company': "Oshodi",
            'jobType': "full-time",
            'location': "Lagos, NG",
            "latitude": 6.5244,
            "longitude": 3.3792,
            "salaryMin": 1500.0,
            "salaryMax": 3000.0,
            'categoryId': str(self.cat.id)
        }

        query = '''
            mutation updateJob($id: UUID!, $input: JobInput!) {
                updateJob(id: $id, input: $input) {
                    job {
                        id
                        title
                        company
                        jobType
                        postedBy {
                            id
                            email
                        }
                    }
                }
            }
        '''

        resp = self.query(
            query=query,
            operation_name="updateJob",
            variables={"id": str(self.job.id),"input": data},
            headers=headers
        )

        self.assertContains(resp, data['title'])
        self.assertContains(resp, data['company'])

    def test_delete_job(self):
        # update job with admin token
        token = self.get_token_for("admin@example.com", "adminpass")

        headers = {"Authorization": f"JWT {token}"}


        query = '''
            mutation deleteJob($id: UUID!) {
                deleteJob(id: $id) {
                    success
                }
            }
        '''

        resp = self.query(
            query=query,
            operation_name="deleteJob",
            variables={"id": str(self.job.id)},
            headers=headers
        )

        data = resp.json()
        self.assertEqual(data['data']['deleteJob'], {'success': True})
        

