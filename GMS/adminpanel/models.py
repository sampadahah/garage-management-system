from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

# Custom User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('mechanic', 'Mechanic'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='customer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# Vehicle model
class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    plate_no = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vehicle'
    
    def __str__(self):
        return f"{self.model} ({self.plate_no})"

# Service Package model
class ServicePackage(models.Model):
    service_package_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estimated_time = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'service_package'
    
    def __str__(self):
        return self.name

# Category model
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'category'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.category_name

# Brand model
class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    
    class Meta:
        db_table = 'brand'
    
    def __str__(self):
        return self.brand_name

# Parts model
class Part(models.Model):
    part_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    compatible_model = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    min_stock_level = models.IntegerField(default=10, validators=[MinValueValidator(1)])
    image = models.ImageField(upload_to='parts/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parts'
    
    def stock_status(self):
        """Determine stock status based on quantity"""
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.quantity <= self.min_stock_level:
            return 'low_stock'
        else:
            return 'in_stock'
    
    def stock_status_display(self):
        """Get display text for stock status"""
        status = self.stock_status()
        if status == 'out_of_stock':
            return 'Out of Stock'
        elif status == 'low_stock':
            return 'Low Stock'
        else:
            return 'In Stock'
    
    def stock_status_color(self):
        """Get color class for stock status"""
        status = self.stock_status()
        if status == 'out_of_stock':
            return 'danger'
        elif status == 'low_stock':
            return 'warning'
        else:
            return 'success'
    
    def __str__(self):
        return f"{self.name} ({self.quantity} units)"

# Appointment model
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    appointment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    service_package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    start_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'appointments'
    
    def __str__(self):
        return f"Appointment #{self.appointment_id} - {self.user.username}"

# Work List model
class WorkList(models.Model):
    JOB_STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    
    work_list_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_lists', limit_choices_to={'role': 'mechanic'})
    job_status = models.CharField(max_length=30, choices=JOB_STATUS_CHOICES, default='assigned')
    notes = models.TextField(blank=True)
    estimated_time = models.CharField(max_length=50, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='work_lists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'work_list'
    
    def __str__(self):
        return f"Work #{self.work_list_id} - {self.get_job_status_display()}"

# Parts Used model
class PartsUsed(models.Model):
    parts_used_id = models.AutoField(primary_key=True)
    work_list = models.ForeignKey(WorkList, on_delete=models.CASCADE, related_name='parts_used')
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'parts_used'
    
    def __str__(self):
        return f"{self.part.name} x{self.quantity}"

# Invoice model
class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]
    
    invoice_id = models.AutoField(primary_key=True)
    work_list = models.ForeignKey(WorkList, on_delete=models.CASCADE, related_name='invoices')
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoices'
    
    def __str__(self):
        return f"Invoice #{self.invoice_id} - ${self.total_amount}"

# Payment model
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    payment_id = models.AutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payment'
    
    def __str__(self):
        return f"Payment #{self.payment_id} - ${self.amount_paid}"

# Vacancy model
class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    
    vacancy_id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=50)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vacancy'
        verbose_name_plural = 'vacancies'
    
    def __str__(self):
        return f"{self.role} ({self.get_status_display()})"

# Applicant model
class Applicant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    
    applicant_id = models.AutoField(primary_key=True)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applicants')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    file_path = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'applicants'
    
    def __str__(self):
        return f"{self.full_name} - {self.vacancy.role}"