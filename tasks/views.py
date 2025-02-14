import logging
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer

logger = logging.getLogger('tasks')
User = get_user_model()

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            logger.info(self.request.user.role)
            if self.request.user.role == "ADMIN":
                return Task.objects.all()
            return Task.objects.filter(user=self.request.user)
        except Exception as e:
            logger.error(f"Error fetching tasks for user {self.request.user}: {e}")
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
            logger.info(f"Task created successfully by user {self.request.user}")
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise e


class TaskRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        logger.info(self)
        if self.request.user.role == "ADMIN":
            return Task.objects.all()
        return Task.objects.filter(user=self.request.user)

    def get_object(self):

        try:
            task = super().get_object()
            if self.request.user.role != "ADMIN" and task.user != self.request.user:
                logger.warning(f"User {self.request.user} tried to access unauthorized task {task.id}")
                raise PermissionDenied({"error": "You do not have permission to access this task."})
            return task
        except Task.DoesNotExist:
            logger.warning(f"Task not found for user {self.request.user}")
            raise NotFound({"error": "Task not found"})

    def update(self, request, *args, **kwargs):

        try:
            task = self.get_object()
            response = super().update(request, *args, **kwargs)
            logger.info(f"Task {task.id} updated by user {self.request.user} (Role: {self.request.user.role})")
            return response
        except PermissionDenied:
            return Response({"error": "You do not have permission to update this task."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return Response({"error": "Error updating task"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):

        try:
            task = self.get_object()
            response = super().delete(request, *args, **kwargs)
            logger.info(f"Task {task.id} deleted by user {self.request.user} (Role: {self.request.user.role})")
            return response
        except PermissionDenied:
            return Response({"error": "You do not have permission to delete this task."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return Response({"error": "Error deleting task"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AssignTaskView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            logger.warning(f"Unauthorized access attempt by {request.user}")
            raise PermissionDenied({"error": "Only admins can assign tasks"})

        task_id = kwargs.get("pk") 
        username = request.data.get("username")

        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            logger.error(f"Task with ID {task_id} not found")
            raise NotFound({"error": "Task not found"})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error(f"User '{username}' not found")
            raise NotFound({"error": "User not found"})

        task.user = user
        task.save()
        logger.info(f"Task '{task.title}' assigned to {user.username} by {request.user}")
        return Response({"message": f"Task '{task.title}' assigned to {user.username}"}, status=status.HTTP_200_OK)