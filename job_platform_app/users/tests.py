import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase
from django.test import TestCase
from job_platform.schema import schema

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


class TestGraphQLAPI(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        self.login_url = reverse("login")  

        # create a normal user
        self.user = User.objects.create_user(
            email="user@example.com", 
            password="userpass", 
            role="user"
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
    
    def test_get_users(self):
        token = self.get_token_for("user@example.com", "userpass")

        headers = {"Authorization": f"JWT {token}"}

        query = '''
            query getUsers {
                users {
                    id
                    email
                    profile {
                        id
                        bio
                    }
                }
            }
        '''

        resp = self.query(
            query=query,
            headers=headers
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, 'profile')

    def test_get_user(self):
        token = self.get_token_for("user@example.com", "userpass")

        headers = {"Authorization": f"JWT {token}"}

        query = '''
            query getUser ($id: UUID!) {
                user (id: $id) {
                    id
                    email
                    profile {
                        id
                        bio
                    }
                }
            }
        '''

        resp = self.query(
            query=query,
            variables={"id": str(self.user.id)},
            headers=headers
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, 'profile')

    def test_unauthorised_user(self):
        query = '''
            query getUsers {
                users {
                    id
                    email
                    profile {
                        id
                        bio
                    }
                }
            }
        '''

        resp = self.query(
            query=query,
        )
        
        self.assertContains(resp, 'User not logged in')

        resp_data = resp.json()
        self.assertEqual(resp_data['data']['users'], None)

