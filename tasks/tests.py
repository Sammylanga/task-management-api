from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Task

User = get_user_model()

class TaskAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            username="admin", password="adminpass", role="ADMIN"
        )
        
        self.regular_user = User.objects.create_user(
            username="user", password="userpass", role="USER"
        )
        
        self.task = Task.objects.create(
            user=self.regular_user, title="Test Task", description="This is a test task", due_date="2025-12-31"
        )

    def test_admin_only_access_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_only_access_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  

    def test_assign_task_to_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(f"/api/tasks/{self.task.id}/assign/", {"username": "admin"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.user, self.admin_user)

    def test_assign_task_to_user_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(f"/api/tasks/{self.task.id}/assign/", {"username": "admin"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.put(f"/api/tasks/{self.task.id}/", {"title": "Updated Task", "description": "Updated description", "due_date": "2025-12-31"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")

    def test_delete_task(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
