from django.urls import path
from .views import TaskListCreateView, TaskRetrieveUpdateDeleteView, AssignTaskView

urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list-create"),
    path("<int:pk>/", TaskRetrieveUpdateDeleteView.as_view(), name="task-detail"),
    path('<int:pk>/assign/', AssignTaskView.as_view(), name='assign-task'),
]
