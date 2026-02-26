from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Slot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]
        unique_together = ("date", "start_time", "end_time")

    def _str_(self):
        status = "Booked" if self.is_booked else "Available"
        return f"{self.date} {self.start_time}-{self.end_time} ({status})"
    

from django.conf import settings
from django.db import models
from django.utils import timezone



class InventoryCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "inventory_categories"

    def __str__(self):
        return self.category_name


class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "brands"

    def __str__(self):
        return self.brand_name


class Part(models.Model):
    part_id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=150)
    compatible_model = models.CharField(max_length=150, blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=5)

    category = models.ForeignKey(
        InventoryCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True
    )

    image = models.ImageField(upload_to="parts/", null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "parts"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def stock_status_display(self):
        if self.quantity == 0:
            return "Out of Stock"
        if self.quantity <= self.min_stock_level:
            return "Low Stock"
        return "In Stock"

    @property
    def stock_status_color(self):
        if self.quantity == 0:
            return "danger"
        if self.quantity <= self.min_stock_level:
            return "warning"
        return "success"


class JobVacancy(models.Model):
    CATEGORY_CHOICES = [
        ("mechanic", "Mechanic"),
        ("assistant", "Assistant"),
        ("reception", "Reception"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    vacancy_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="other")
    title = models.CharField(max_length=150)
    openings = models.PositiveIntegerField(default=1)
    deadline = models.DateField(null=True, blank=True)

    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "job_vacancies"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "title", "deadline"],
                name="unique_job_by_category_title_deadline",
        )
    ]

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"





class WorkList(models.Model):
    JOB_STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    work_list_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)

    job_status = models.CharField(
        max_length=20,
        choices=JOB_STATUS_CHOICES,
        default="assigned"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "work_list"
        ordering = ["-created_at"]
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
