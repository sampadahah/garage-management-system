from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class StaffRole(models.Model):
    """Staff roles with permissions"""
    ROLE_CHOICES = (
        ('Manager', 'Manager'),
        ('Trainer', 'Trainer'),
        ('Receptionist', 'Receptionist'),
        ('Maintenance', 'Maintenance'),
    )
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    # Permissions
    can_manage_staff = models.BooleanField(default=False)
    can_manage_customers = models.BooleanField(default=False)
    can_manage_schedules = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Staff Role"
        verbose_name_plural = "Staff Roles"


class Staff(models.Model):
    """Staff member profile"""
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.ForeignKey(StaffRole, on_delete=models.SET_NULL, null=True, related_name='staff_members')
    
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.employee_id}"
    
    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"
        ordering = ['-created_at']


class Schedule(models.Model):
    """Staff work schedules"""
    SHIFT_CHOICES = (
        ('Morning', 'Morning (6 AM - 2 PM)'),
        ('Afternoon', 'Afternoon (2 PM - 10 PM)'),
        ('Evening', 'Evening (10 PM - 6 AM)'),
        ('Full Day', 'Full Day (9 AM - 6 PM)'),
    )
    
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.staff.user.name} - {self.day_of_week} ({self.shift})"
    
    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
        ordering = ['day_of_week', 'start_time']
        unique_together = ['staff', 'day_of_week', 'shift']


class LeaveRequest(models.Model):
    """Staff leave requests"""
    LEAVE_TYPE_CHOICES = (
        ('Sick', 'Sick Leave'),
        ('Casual', 'Casual Leave'),
        ('Vacation', 'Vacation'),
        ('Emergency', 'Emergency'),
    )
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.staff.user.name} - {self.leave_type} ({self.status})"
    
    class Meta:
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"
        ordering = ['-created_at']
