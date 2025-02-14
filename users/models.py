from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    USER = "USER", "User"

class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )

    def __str__(self):
        return self.username
