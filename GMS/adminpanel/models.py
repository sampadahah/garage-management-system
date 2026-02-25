from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.category_name


class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "brand"

    def __str__(self):
        return self.brand_name


class Part(models.Model):
    part_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    compatible_model = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    min_stock_level = models.IntegerField(default=10, validators=[MinValueValidator(1)])

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)

    image = models.ImageField(upload_to="parts/", blank=True, null=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "parts"

    def stock_status(self):
        if self.quantity == 0:
            return "out_of_stock"
        if self.quantity <= self.min_stock_level:
            return "low_stock"
        return "in_stock"

    def stock_status_display(self):
        s = self.stock_status()
        return "Out of Stock" if s == "out_of_stock" else ("Low Stock" if s == "low_stock" else "In Stock")

    def stock_status_color(self):
        s = self.stock_status()
        return "danger" if s == "out_of_stock" else ("warning" if s == "low_stock" else "success")

    def __str__(self):
        return self.name


# Only for your jobs template: work.appointment.service_package.name
class ServicePackage(models.Model):
    service_package_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "service_package"

    def __str__(self):
        return self.name


class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    service_package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE)

    class Meta:
        db_table = "appointments"

    def __str__(self):
        return f"Appointment #{self.appointment_id}"


class WorkList(models.Model):
    JOB_STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
    ]

    work_list_id = models.AutoField(primary_key=True)

    # SAFE: never import friend model directly
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="work_lists",
        limit_choices_to={"role": "Mechanic"},  # friend uses "Mechanic"
    )

    job_status = models.CharField(max_length=30, choices=JOB_STATUS_CHOICES, default="assigned")
    estimated_time = models.CharField(max_length=50, blank=True)

    # optional appointment (your create_job template says optional)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "work_list"

    def __str__(self):
        return f"Work #{self.work_list_id}"
        

class Vacancy(models.Model):
    STATUS_CHOICES = (
        ("open", "Open"),
        ("closed", "Closed"),
    )

    CATEGORY_CHOICES = (
        ("mechanic", "Mechanic"),
        ("washing", "Car Washing"),
        ("accountant", "Accountant"),
        ("receptionist", "Receptionist"),
        ("manager", "Service Manager"),
        ("helper", "Helper"),
        ("other", "Other"),
    )

    vacancy_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=120)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    openings = models.PositiveIntegerField(default=1)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vacancy"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title