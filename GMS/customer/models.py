# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, name, password, **extra_fields)
    
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

    is_verified = models.BooleanField(default=False)
    

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()
    
    def __str__(self):
        return f"{self.name} ({self.role})"
    
