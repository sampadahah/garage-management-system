from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Staff, StaffRole, Schedule, LeaveRequest
from .forms import (
    StaffLoginForm, StaffCreationForm, StaffUpdateForm, 
    UserUpdateForm, ScheduleForm, LeaveRequestForm, StaffRoleForm
)

User = get_user_model()


# Authentication Views
def staff_login(request):
    if request.user.is_authenticated and hasattr(request.user, 'staff_profile'):
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # Check if user is staff
                if hasattr(user, 'staff_profile'):
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.name}!')
                    return redirect('staff_dashboard')
                else:
                    messages.error(request, 'You do not have staff access.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = StaffLoginForm()
    
    return render(request, 'staff/login.html', {'form': form})


@login_required
def staff_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('staff_login')


# Dashboard
@login_required
def staff_dashboard(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied. Staff only.')
        return redirect('login')
    
    staff = request.user.staff_profile
    
    # Get today's schedule
    today = timezone.now().strftime('%A')
    today_schedule = Schedule.objects.filter(staff=staff, day_of_week=today, is_active=True)
    
    # Get pending leave requests
    pending_leaves = LeaveRequest.objects.filter(staff=staff, status='Pending')
    
    # Get upcoming schedules
    upcoming_schedules = Schedule.objects.filter(staff=staff, is_active=True)[:5]
    
    context = {
        'staff': staff,
        'today_schedule': today_schedule,
        'pending_leaves': pending_leaves,
        'upcoming_schedules': upcoming_schedules,
    }
    
    return render(request, 'staff/dashboard.html', context)


# Staff CRUD Operations
@login_required
def staff_list(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    # Check permission
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_staff:
        messages.error(request, 'You do not have permission to manage staff.')
        return redirect('staff_dashboard')
    
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    staff_members = Staff.objects.select_related('user', 'role').all()
    
    if query:
        staff_members = staff_members.filter(
            Q(user__name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(user__email__icontains=query)
        )
    
    if status_filter:
        staff_members = staff_members.filter(status=status_filter)
    
    context = {
        'staff_members': staff_members,
        'query': query,
        'status_filter': status_filter,
    }
    
    return render(request, 'staff/staff_list.html', context)


@login_required
def staff_create(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_staff:
        messages.error(request, 'You do not have permission to create staff.')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User(
                email=form.cleaned_data['email'].lower().strip(),
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                role='Mechanic',  # Staff role in Users model
                is_active=True,
                is_verified=True,
            )
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Create staff profile
            staff = Staff.objects.create(
                user=user,
                employee_id=form.cleaned_data['employee_id'],
                role=form.cleaned_data['role'],
                hire_date=form.cleaned_data['hire_date'],
                salary=form.cleaned_data.get('salary'),
                department=form.cleaned_data.get('department', ''),
                status='Active'
            )
            
            messages.success(request, f'Staff member {user.name} created successfully!')
            return redirect('staff_list')
    else:
        form = StaffCreationForm()
    
    return render(request, 'staff/staff_form.html', {'form': form, 'action': 'Create'})


@login_required
def staff_detail(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff = get_object_or_404(Staff, pk=pk)
    schedules = Schedule.objects.filter(staff=staff, is_active=True)
    leave_requests = LeaveRequest.objects.filter(staff=staff).order_by('-created_at')[:10]
    
    context = {
        'staff': staff,
        'schedules': schedules,
        'leave_requests': leave_requests,
    }
    
    return render(request, 'staff/staff_detail.html', context)


@login_required
def staff_update(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff = get_object_or_404(Staff, pk=pk)
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_staff:
        # Allow staff to update their own profile
        if request.user.staff_profile != staff:
            messages.error(request, 'You do not have permission to update this staff member.')
            return redirect('staff_dashboard')
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=staff.user)
        staff_form = StaffUpdateForm(request.POST, instance=staff)
        
        if user_form.is_valid() and staff_form.is_valid():
            user_form.save()
            staff_form.save()
            messages.success(request, 'Staff information updated successfully!')
            return redirect('staff_detail', pk=staff.pk)
    else:
        user_form = UserUpdateForm(instance=staff.user)
        staff_form = StaffUpdateForm(instance=staff)
    
    context = {
        'user_form': user_form,
        'staff_form': staff_form,
        'staff': staff,
        'action': 'Update'
    }
    
    return render(request, 'staff/staff_update.html', context)


@login_required
def staff_delete(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_staff:
        messages.error(request, 'You do not have permission to delete staff.')
        return redirect('staff_dashboard')
    
    staff = get_object_or_404(Staff, pk=pk)
    
    if request.method == 'POST':
        user = staff.user
        staff.delete()
        user.delete()
        messages.success(request, 'Staff member deleted successfully!')
        return redirect('staff_list')
    
    return render(request, 'staff/staff_confirm_delete.html', {'staff': staff})


# Schedule Management
@login_required
def schedule_list(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff_role = request.user.staff_profile.role
    
    if staff_role and staff_role.can_manage_schedules:
        # Managers can see all schedules
        schedules = Schedule.objects.select_related('staff__user').all()
    else:
        # Staff can only see their own schedules
        schedules = Schedule.objects.filter(staff=request.user.staff_profile)
    
    day_filter = request.GET.get('day', '')
    if day_filter:
        schedules = schedules.filter(day_of_week=day_filter)
    
    context = {
        'schedules': schedules,
        'day_filter': day_filter,
        'can_manage': staff_role and staff_role.can_manage_schedules,
    }
    
    return render(request, 'staff/schedule_list.html', context)


@login_required
def schedule_create(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_schedules:
        messages.error(request, 'You do not have permission to create schedules.')
        return redirect('schedule_list')
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule created successfully!')
            return redirect('schedule_list')
    else:
        form = ScheduleForm()
    
    return render(request, 'staff/schedule_form.html', {'form': form, 'action': 'Create'})


@login_required
def schedule_update(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    schedule = get_object_or_404(Schedule, pk=pk)
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_schedules:
        messages.error(request, 'You do not have permission to update schedules.')
        return redirect('schedule_list')
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully!')
            return redirect('schedule_list')
    else:
        form = ScheduleForm(instance=schedule)
    
    return render(request, 'staff/schedule_form.html', {'form': form, 'action': 'Update', 'schedule': schedule})


@login_required
def schedule_delete(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_schedules:
        messages.error(request, 'You do not have permission to delete schedules.')
        return redirect('schedule_list')
    
    schedule = get_object_or_404(Schedule, pk=pk)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('schedule_list')
    
    return render(request, 'staff/schedule_confirm_delete.html', {'schedule': schedule})


# Leave Request Management
@login_required
def leave_request_list(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    # Admin can see all leave requests, staff can only see their own
    if request.user.is_superuser:
        leave_requests = LeaveRequest.objects.select_related('staff__user').all()
        can_manage = True
    else:
        leave_requests = LeaveRequest.objects.filter(staff=request.user.staff_profile)
        can_manage = False
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)
    
    context = {
        'leave_requests': leave_requests,
        'status_filter': status_filter,
        'can_manage': can_manage,
    }
    
    return render(request, 'staff/leave_request_list.html', context)


@login_required
def leave_request_create(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.staff = request.user.staff_profile
            leave_request.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('leave_request_list')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'staff/leave_request_form.html', {'form': form, 'action': 'Create'})


@login_required
def leave_request_detail(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Check if user can view this leave request
    if not request.user.is_superuser and leave_request.staff != request.user.staff_profile:
        messages.error(request, 'You do not have permission to view this leave request.')
        return redirect('leave_request_list')
    
    return render(request, 'staff/leave_request_detail.html', {'leave_request': leave_request})


@login_required
def leave_request_approve(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    # Only superuser/admin can approve
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can approve leave requests.')
        return redirect('leave_request_list')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        leave_request.status = 'Approved'
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.save()
        messages.success(request, 'Leave request approved!')
        return redirect('leave_request_list')
    
    return render(request, 'staff/leave_request_approve.html', {'leave_request': leave_request})


@login_required
def leave_request_reject(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    # Only superuser/admin can reject
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can reject leave requests.')
        return redirect('leave_request_list')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        leave_request.status = 'Rejected'
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.rejection_reason = rejection_reason
        leave_request.save()
        messages.success(request, 'Leave request rejected.')
        return redirect('leave_request_list')
    
    return render(request, 'staff/leave_request_reject.html', {'leave_request': leave_request})


@login_required
def leave_request_delete(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Staff can delete their own pending requests, admin can delete any
    if not request.user.is_superuser and leave_request.staff != request.user.staff_profile:
        messages.error(request, 'You do not have permission to delete this leave request.')
        return redirect('leave_request_list')
    
    # Only allow deletion of pending requests
    if leave_request.status != 'Pending' and not request.user.is_superuser:
        messages.error(request, 'You can only delete pending leave requests.')
        return redirect('leave_request_list')
    
    if request.method == 'POST':
        leave_request.delete()
        messages.success(request, 'Leave request deleted successfully!')
        return redirect('leave_request_list')
    
    return render(request, 'staff/leave_request_confirm_delete.html', {'leave_request': leave_request})


# Staff Role Management
@login_required
def role_list(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_staff:
        messages.error(request, 'You do not have permission to manage roles.')
        return redirect('staff_dashboard')
    
    roles = StaffRole.objects.all()
    return render(request, 'staff/role_list.html', {'roles': roles})


@login_required
def role_create(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_staff:
        messages.error(request, 'You do not have permission to create roles.')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        form = StaffRoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role created successfully!')
            return redirect('role_list')
    else:
        form = StaffRoleForm()
    
    return render(request, 'staff/role_form.html', {'form': form, 'action': 'Create'})


@login_required
def role_update(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_staff:
        messages.error(request, 'You do not have permission to update roles.')
        return redirect('staff_dashboard')
    
    role = get_object_or_404(StaffRole, pk=pk)
    
    if request.method == 'POST':
        form = StaffRoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role updated successfully!')
            return redirect('role_list')
    else:
        form = StaffRoleForm(instance=role)
    
    return render(request, 'staff/role_form.html', {'form': form, 'action': 'Update', 'role': role})


@login_required
def role_delete(request, pk):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied.')
        return redirect('staff_dashboard')
    
    staff_role = request.user.staff_profile.role
    if not staff_role or not staff_role.can_manage_staff:
        messages.error(request, 'You do not have permission to delete roles.')
        return redirect('staff_dashboard')
    
    role = get_object_or_404(StaffRole, pk=pk)
    
    if request.method == 'POST':
        role.delete()
        messages.success(request, 'Role deleted successfully!')
        return redirect('role_list')
    
    return render(request, 'staff/role_confirm_delete.html', {'role': role})
