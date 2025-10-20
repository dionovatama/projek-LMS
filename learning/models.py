from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('guru', 'Guru'),
        ('murid', 'Murid'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="murid")

    def __str__(self):
        return f"{self.username} ({self.role})"
