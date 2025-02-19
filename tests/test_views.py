from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tasks.models import Task

User = get_user_model()


class TaskManagementIntegrationTests(TestCase):
    def setUp(self):
        """Setup test users and API client"""
        self.client = APIClient()

        # Create users
        self.admin_user = User.objects.create_user(username="adminuser", password="adminpass", role="ADMIN")
        self.regular_user = User.objects.create_user(username="regularuser", password="regularpass", role="USER")

        # Get JWT token for admin
        admin_response = self.client.post("/api/auth/login/", {"username": "adminuser", "password": "adminpass"})
        self.admin_token = admin_response.data["access"]

        # Get JWT token for regular user
        user_response = self.client.post("/api/auth/login/", {"username": "regularuser", "password": "regularpass"})
        self.user_token = user_response.data["access"]

        # Authenticate client as admin by default
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

        # Create a test task for the regular user
        self.task = Task.objects.create(
            user=self.regular_user,
            title="Test Task",
            description="This is a test task",
            due_date="2025-12-31"
        )

    def authenticate_as_regular_user(self):
        """Switch authentication to the regular user"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

    def authenticate_as_admin(self):
        """Switch authentication to the admin user"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

    # 🟢 CREATE TASK
    def test_regular_user_can_create_task(self):
        """Test if a regular user can create a task"""
        self.authenticate_as_regular_user()
        response = self.client.post(
            "/api/tasks/",
            {"title": "New Task", "description": "A new test task", "due_date": "2025-12-31"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # 🟢 READ TASKS
    def test_admin_can_see_all_tasks(self):
        """Test if an admin can view all tasks"""
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_can_only_see_their_tasks(self):
        """Test if a regular user can only see their own tasks"""
        self.authenticate_as_regular_user()
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Regular user should only see their task

    # 🟢 UPDATE TASK
    def test_task_update(self):
        """Test if a user can update their own task"""
        self.authenticate_as_regular_user()
        response = self.client.put(
            f"/api/tasks/{self.task.id}/",
            {"title": "Updated Task", "description": "Updated description", "due_date": "2025-12-31"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_update_others_tasks(self):
        """Test that a regular user cannot update another user’s task"""
        self.authenticate_as_admin()  # Admin owns the client session
        other_user_task = Task.objects.create(
            user=self.admin_user, title="Admin Task", description="Admin's task", due_date="2025-12-31"
        )

        self.authenticate_as_regular_user()
        response = self.client.put(
            f"/api/tasks/{other_user_task.id}/",
            {"title": "Hacked Task", "description": "Unauthorized update", "due_date": "2025-12-31"},
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 🟢 DELETE TASK
    def test_task_deletion_by_owner(self):
        """Test if a user can delete their own task"""
        self.authenticate_as_regular_user()
        response = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_delete_any_task(self):
        """Test if an admin can delete any task"""
        response = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_delete_others_tasks(self):
        """Test that a regular user cannot delete another user’s task"""
        self.authenticate_as_admin()
        other_user_task = Task.objects.create(
            user=self.admin_user, title="Admin Task", description="Admin's task", due_date="2025-12-31"
        )

        self.authenticate_as_regular_user()
        response = self.client.delete(f"/api/tasks/{other_user_task.id}/")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 🟢 ASSIGN TASKS (Only Admin)
    def test_admin_can_assign_task(self):
        """Test if an admin can assign a task to another user"""
        new_user = User.objects.create_user(username="newuser", password="newpass", role="USER")

        response = self.client.patch(
            f"/api/tasks/{self.task.id}/assign/",
            {"username": new_user.username},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.user, new_user)

    def test_regular_user_cannot_assign_task(self):
        """Test that a regular user cannot assign a task"""
        self.authenticate_as_regular_user()
        response = self.client.patch(
            f"/api/tasks/{self.task.id}/assign/",
            {"username": "adminuser"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 🟢 PERMISSIONS
    def test_unauthenticated_user_cannot_access_tasks(self):
        """Test that an unauthenticated user cannot access the task list"""
        self.client.credentials()  # Remove authentication
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


if __name__ == "__main__":
    import unittest
    unittest.main()
