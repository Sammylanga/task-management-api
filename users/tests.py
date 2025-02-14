from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from tasks.models import Task 

User = get_user_model()

class UserTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(username="admin", password="adminpass", role="ADMIN")
        self.regular_user = User.objects.create_user(username="user", password="userpass", role="USER")

        self.task = Task.objects.create(
            user=self.regular_user,
            title="Test Task",
            description="This is a test task",
            due_date=datetime.now() + timedelta(days=7)  
        )

    def test_register_user(self):

        data = {
            "username": "new_user",
            "password": "newpassword",
            "role": "USER"
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):

        data = {
            "username": "user",
            "password": "userpass"
        }
        response = self.client.post("/api/auth/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials(self):

        data = {
            "username": "user",
            "password": "wrongpassword"
        }
        response = self.client.post("/api/auth/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_only_access_as_admin(self):

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/auth/admin-only/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_only_access_as_regular_user(self):

        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/auth/admin-only/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assign_task_to_user_as_admin(self):

        self.client.force_authenticate(user=self.admin_user)
        data = {
            "username": "user",
            "task_id": self.task.id
        }
        response = self.client.put("/api/tasks/1/assign/", data, format="json")  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], f"Task '{self.task.title}' assigned to user")
        self.task.refresh_from_db()
        self.assertEqual(self.task.user, self.regular_user)
