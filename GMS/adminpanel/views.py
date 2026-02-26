from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Slot, Service
from .forms import SlotForm, ServiceForm
from datetime import date, datetime, timedelta
from django.http import HttpResponseForbidden


def is_staff_or_superuser(u):
    return u.is_authenticated and (u.is_staff or u.is_superuser)

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def admin_dashboard(request):
    """Admin dashboard showing overview"""
    today = date.today()
    total_slots = Slot.objects.count()
    available_slots = Slot.objects.filter(is_booked=False).count()
    booked_slots = Slot.objects.filter(is_booked=True).count()
    today_slots = Slot.objects.filter(date=today).count()
    
    context = {
        'total_slots': total_slots,
        'available_slots': available_slots,
        'booked_slots': booked_slots,
        'today_slots': today_slots,
    }
    return render(request, "adminpanel/dashboard.html", context)

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def slot_calendar(request):
    """Show calendar and slots for selected date or all slots"""
    selected_date = request.GET.get("date")
    selected_date_obj = None
    
    if selected_date:
        try:
            selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            # Filter by specific date
            slots = Slot.objects.filter(date=selected_date_obj).order_by("start_time")
        except Exception:
            # If date parsing fails, show all slots
            slots = Slot.objects.all().order_by("date", "start_time")
    else:
        # No date selected, show all slots
        slots = Slot.objects.all().order_by("date", "start_time")
    
    context = {
        "selected_date": selected_date_obj,
        "slots": slots,
        "showing_all": selected_date_obj is None,
    }
    return render(request, "adminpanel/slot_calendar.html", context)

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def toggle_slot_status(request, slot_id):
    """Toggle slot status between available and booked"""
    if request.method == "POST":
        slot = Slot.objects.get(id=slot_id)
        slot.is_booked = not slot.is_booked
        slot.save()
        
        status = "booked" if slot.is_booked else "available"
        messages.success(request, f"Slot status changed to {status}.")
        
        # Redirect back to calendar with date filter if it was set
        date_param = request.POST.get('date_filter', '')
        if date_param:
            return redirect(reverse("adminpanel:slot_calendar") + f"?date={date_param}")
        return redirect("adminpanel:slot_calendar")
    
    return redirect("adminpanel:slot_calendar")

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def add_slot(request):
    """Add a new slot"""
    if request.method == "POST":
        form = SlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.created_by = request.user
            try:
                slot.save()
                messages.success(request, "Slot added successfully.")
                return redirect(reverse("adminpanel:slot_calendar") + f"?date={slot.date}")
            except Exception as e:
                messages.error(request, f"Could not add slot: {e}")
    else:
        form = SlotForm()
    return render(request, "adminpanel/add_slot.html", {"form": form})

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def customers(request):
    """View all customers"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Get all customers (non-staff users)
    customers_list = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
    
    context = {
        'customers': customers_list,
        'total_customers': customers_list.count(),
    }
    return render(request, "adminpanel/customers.html", context)

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def reports(request):
    """View reports page with download options"""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Get counts for display
    total_slots = Slot.objects.count()
    total_customers = User.objects.filter(is_staff=False, is_superuser=False).count()
    booked_slots = Slot.objects.filter(is_booked=True).count()
    
    context = {
        'total_slots': total_slots,
        'total_customers': total_customers,
        'booked_slots': booked_slots,
    }
    return render(request, "adminpanel/reports.html", context)

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def download_slots_report(request):
    """Download slots report as CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="slots_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Start Time', 'End Time', 'Status', 'Created By', 'Created At'])
    
    slots = Slot.objects.all().order_by('-date', 'start_time')
    for slot in slots:
        writer.writerow([
            slot.date.strftime('%Y-%m-%d'),
            slot.start_time.strftime('%H:%M'),
            slot.end_time.strftime('%H:%M'),
            'Booked' if slot.is_booked else 'Available',
            slot.created_by.email if slot.created_by else 'N/A',
            slot.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def download_customers_report(request):
    """Download customers report as CSV"""
    import csv
    from django.http import HttpResponse
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Address', 'Role', 'Verified', 'Active', 'Date Joined'])
    
    customers = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
    for customer in customers:
        writer.writerow([
            customer.name,
            customer.email,
            customer.phone or 'N/A',
            customer.address or 'N/A',
            customer.role,
            'Yes' if customer.is_verified else 'No',
            'Yes' if customer.is_active else 'No',
            customer.date_joined.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def download_bookings_report(request):
    """Download bookings report as CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Start Time', 'End Time', 'Created By', 'Booked At'])
    
    booked_slots = Slot.objects.filter(is_booked=True).order_by('-date', 'start_time')
    for slot in booked_slots:
        writer.writerow([
            slot.date.strftime('%Y-%m-%d'),
            slot.start_time.strftime('%H:%M'),
            slot.end_time.strftime('%H:%M'),
            slot.created_by.email if slot.created_by else 'N/A',
            slot.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

@login_required
@user_passes_test(is_staff_or_superuser, login_url='/customer/login/')
def download_all_reports(request):
    """Download all reports as ZIP file"""
    import csv
    import zipfile
    import io
    from django.http import HttpResponse
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Create in-memory zip file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Slots Report
        slots_data = io.StringIO()
        slots_writer = csv.writer(slots_data)
        slots_writer.writerow(['Date', 'Start Time', 'End Time', 'Status', 'Created By', 'Created At'])
        slots = Slot.objects.all().order_by('-date', 'start_time')
        for slot in slots:
            slots_writer.writerow([
                slot.date.strftime('%Y-%m-%d'),
                slot.start_time.strftime('%H:%M'),
                slot.end_time.strftime('%H:%M'),
                'Booked' if slot.is_booked else 'Available',
                slot.created_by.email if slot.created_by else 'N/A',
                slot.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        zip_file.writestr('slots_report.csv', slots_data.getvalue())
        
        # Customers Report
        customers_data = io.StringIO()
        customers_writer = csv.writer(customers_data)
        customers_writer.writerow(['Name', 'Email', 'Phone', 'Address', 'Role', 'Verified', 'Active', 'Date Joined'])
        customers = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
        for customer in customers:
            customers_writer.writerow([
                customer.name,
                customer.email,
                customer.phone or 'N/A',
                customer.address or 'N/A',
                customer.role,
                'Yes' if customer.is_verified else 'No',
                'Yes' if customer.is_active else 'No',
                customer.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            ])
        zip_file.writestr('customers_report.csv', customers_data.getvalue())
        
        # Bookings Report
        bookings_data = io.StringIO()
        bookings_writer = csv.writer(bookings_data)
        bookings_writer.writerow(['Date', 'Start Time', 'End Time', 'Created By', 'Booked At'])
        booked_slots = Slot.objects.filter(is_booked=True).order_by('-date', 'start_time')
        for slot in booked_slots:
            bookings_writer.writerow([
                slot.date.strftime('%Y-%m-%d'),
                slot.start_time.strftime('%H:%M'),
                slot.end_time.strftime('%H:%M'),
                slot.created_by.email if slot.created_by else 'N/A',
                slot.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        zip_file.writestr('bookings_report.csv', bookings_data.getvalue())
    
    # Prepare response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="all_reports.zip"'
    
    return response

# adminpanel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Service
from .forms import ServiceForm

def admin_service_list(request):
    services = Service.objects.all()
    return render(request, 'adminpanel/service_list.html', {'services': services})

def admin_add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_service_list')
    else:
        form = ServiceForm()
    return render(request, 'adminpanel/service_form.html', {'form': form, 'title': 'Add Service'})

def admin_edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('admin_service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'adminpanel/service_form.html', {'form': form, 'title': 'Edit Service'})

def admin_delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('admin_service_list')
    return render(request, 'adminpanel/service_confirm_delete.html', {'service': service})