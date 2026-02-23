# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    ROLE_CHOICES = (
        ("Admin", "Admin"),
        ("Customer", "Customer"),
        ("Mechanic", "Mechanic"),
    )

    # Use email as the login field (more standard for your system)
    username = None
    email = models.EmailField(unique=True)

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Customer")
    status = models.CharField(max_length=20, default="Active")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return f"{self.name} ({self.role})"