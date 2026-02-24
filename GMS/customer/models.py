# Create your models here.
from django.db import models
from django.conf import settings
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
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", "Admin") 

        return self.create_user(email, name, password, **extra_fields)
    
class Users(AbstractUser):
    ROLE_CHOICES = (
        ("Admin", "Admin"),
        ("Customer", "Customer"),
        ("Mechanic", "Mechanic"),
    )

    
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
    

class Vehicle(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicles"
    )
    model = models.CharField(max_length=120)
    year = models.PositiveIntegerField()
    plate_no = models.CharField(max_length=20)
    image = models.ImageField(upload_to="vehicles/",blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "plate_no")  # same user can't duplicate plate
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.model} ({self.plate_no})"