from django.contrib import admin
from .models import Staff, StaffRole, Schedule, LeaveRequest


@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'can_manage_staff', 'can_manage_customers', 'can_manage_schedules', 'can_view_reports']
    list_filter = ['name']
    search_fields = ['name', 'description']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'role', 'department', 'hire_date', 'status']
    list_filter = ['status', 'role', 'department']
    search_fields = ['employee_id', 'user__name', 'user__email']
    date_hierarchy = 'hire_date'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['staff', 'day_of_week', 'shift', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'shift', 'is_active']
    search_fields = ['staff__user__name', 'staff__employee_id']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['staff__user__name', 'staff__employee_id', 'reason']
    date_hierarchy = 'created_at'
