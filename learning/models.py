from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ("guru", "Guru"),
        ("siswa", "Siswa"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="siswa")

    def __str__(self):
        return f"{self.username} ({self.role})"
