from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Slot
from .forms import SlotForm
from datetime import date, datetime, timedelta
from django.http import HttpResponseForbidden

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model

from .forms import JobVacancyForm, PartForm
from .models import JobVacancy, Part, WorkList

from django.shortcuts import redirect

from .models import InventoryCategory, Brand


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



def admin_login(request):
    """Admin login view that checks for staff/superuser status"""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect("dashboard")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            if not (user.is_staff or user.is_superuser):
                messages.error(request, "Access denied. Admin privileges required.")
                return render(request, "login.html")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "login.html")
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Access denied. Admin privileges required.")
        else:
            messages.error(request, "Invalid email or password.")
        
        return render(request, "login.html")
    
    return render(request, "login.html")


def is_admin(user):
    # adjust if you have your own role field
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    # Inventory stats
    total_items = Part.objects.count()
    low_stock_items = Part.objects.filter(quantity__gt=0, quantity__lte=F("min_stock_level")).count()
    out_of_stock_items = Part.objects.filter(quantity=0).count()

    # Recent inventory for table
    recent_inventory = Part.objects.all().order_by("-created_at")[:5]

    # Jobs stats (WorkList)
    total_jobs = WorkList.objects.count()
    pending_jobs = WorkList.objects.filter(job_status="assigned").count()
    in_progress_jobs = WorkList.objects.filter(job_status="in_progress").count()

    recent_jobs = WorkList.objects.select_related("user", "appointment").order_by("-created_at")[:5]

    # Customers stats (if you have Customer model later, replace this)
    # For now we count non-staff users as customers
    from django.contrib.auth import get_user_model
    User = get_user_model()

    total_customers = User.objects.filter(is_staff=False, is_superuser=False).count()

    today = timezone.localdate()
    new_customers_today = User.objects.filter(
        is_staff=False, is_superuser=False,
        date_joined__date=today
    ).count()

    # Appointments stats (you can replace later)
    pending_appointments = 0

    context = {
        "page_title": "Dashboard",
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "recent_inventory": recent_inventory,
        "total_jobs": total_jobs,
        "recent_jobs": recent_jobs,
        "total_customers": total_customers,
        "new_customers_today": new_customers_today,
        "pending_jobs": pending_jobs,
        "in_progress_jobs": in_progress_jobs,
        "pending_appointments": pending_appointments,
    }
    return render(request, "adminpanel/dashboard.html", context)


# -------- Inventory (needed for your dashboard links) --------
@login_required
@user_passes_test(is_admin)
def inventory(request):
    search_query = request.GET.get("search", "").strip()
    qs = Part.objects.select_related("category", "brand").all()

    if search_query:
            qs = qs.filter(
        Q(name__icontains=search_query) |
        Q(compatible_model__icontains=search_query) |
        Q(category__category_name__icontains=search_query) |
        Q(brand__brand_name__icontains=search_query)
    )

    out_of_stock_items = qs.filter(quantity=0).count()

    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page")
    inventory_items = paginator.get_page(page_number)

    return render(
        request,
        "adminpanel/inventory.html",
        {
            "page_title": "Inventory",
            "inventory_items": inventory_items,
            "search_query": search_query,
            "out_of_stock_items": out_of_stock_items,
        },
    )


@login_required
@user_passes_test(is_admin)
def add_inventory_item(request):
    if request.method == "POST":
        form = PartForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:inventory")
    else:
        form = PartForm()

    return render(request, "adminpanel/add_inventory_item.html", {"page_title": "Inventory", "form": form})


@login_required
@user_passes_test(is_admin)
def edit_inventory_item(request, part_id):
    item = get_object_or_404(Part, part_id=part_id)

    if request.method == "POST":
        form = PartForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:inventory")
    else:
        form = PartForm(instance=item)

    return render(
        request,
        "adminpanel/edit_inventory_item.html",
        {"page_title": "Inventory", "form": form, "item": item},
    )


@login_required
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
def delete_inventory_item(request, part_id):
    item = get_object_or_404(Part, part_id=part_id)

    if request.method == "POST":
        item.delete()
        return redirect("adminpanel:inventory")  

    return render(
        request,
        "adminpanel/delete_inventory_item.html",
        {"page_title": "Inventory", "item": item},
    )


@login_required
@user_passes_test(is_admin)
def item_details(request, part_id):
    item = get_object_or_404(Part.objects.select_related("category", "brand"), part_id=part_id)
    return render(request, "adminpanel/item_details.html", {"page_title": "Inventory", "item": item})


# -------- Jobs (Vacancy) --------
@login_required
@user_passes_test(is_admin)
def jobs(request):
    vacancies = JobVacancy.objects.all()
    return render(request, "adminpanel/jobs.html", {"page_title": "Jobs", "vacancies": vacancies})


@login_required
@user_passes_test(is_admin)
def create_job(request):
    if request.method == "POST":
        form = JobVacancyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:jobs")
    else:
        form = JobVacancyForm()

    return render(
        request,
        "adminpanel/create_job.html",
        {"page_title": "Jobs", "form": form},
    )


# -------- Logout --------
@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    if request.method in ["POST", "GET"]:
        logout(request)
        return redirect("login")

# -------- Leaves (if you have staff branch merged) --------
try:
    from staff.models import LeaveApplication
except Exception:
    LeaveApplication = None
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@login_required
@user_passes_test(is_admin)
def leaves(request):
    if LeaveApplication is None:
        # staff branch not merged yet
        return render(
            request,
            "adminpanel/leaves_not_ready.html",
            {"page_title": "Leaves"},
        )

    leaves_qs = LeaveApplication.objects.select_related("user").order_by("-applied_at")
    return render(
        request,
        "adminpanel/leaves.html",
        {"page_title": "Leaves", "leaves": leaves_qs},
    )


@login_required
@user_passes_test(is_admin)
def decide_leave(request, leave_id, action):
    if LeaveApplication is None:
        return redirect("adminpanel:leaves")

    leave = get_object_or_404(LeaveApplication, leave_id=leave_id)

    if action == "approve":
        leave.status = "approved"
    elif action == "reject":
        leave.status = "rejected"
    else:
        return redirect("adminpanel:leaves")

    leave.decided_at = timezone.now()
    leave.save(update_fields=["status", "decided_at"])

    return redirect("adminpanel:leaves")


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

# ----------- Categories -----------
@login_required
@user_passes_test(is_admin)
def categories(request):
    categories = InventoryCategory.objects.all().order_by("category_name")
    return render(request, "adminpanel/categories.html", {
        "page_title": "Categories",
        "categories": categories,
    })

@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == "POST":
        name = (request.POST.get("category_name") or "").strip()
        if name:
            InventoryCategory.objects.get_or_create(category_name=name)
            return redirect("adminpanel:categories")

    return render(request, "adminpanel/add_category.html", {"page_title": "Categories"})

@login_required
@user_passes_test(is_admin)
def delete_category(request, category_id):
    category = get_object_or_404(InventoryCategory, category_id=category_id)
    category.delete()
    return redirect("adminpanel:categories")

# ----------- Brands -----------
@login_required
@user_passes_test(is_admin)
def brands(request):
    brands = Brand.objects.all().order_by("brand_name")
    return render(request, "adminpanel/brands.html", {
        "page_title": "Brands",
        "brands": brands,
    })

@login_required
@user_passes_test(is_admin)
def add_brand(request):
    if request.method == "POST":
        name = (request.POST.get("brand_name") or "").strip()
        if name:
            Brand.objects.get_or_create(brand_name=name)
            return redirect("adminpanel:brands")

    return render(request, "adminpanel/add_brand.html", {"page_title": "Brands"})

@login_required
@user_passes_test(is_admin)
def delete_brand(request, brand_id):
    brand = get_object_or_404(Brand, brand_id=brand_id)
    brand.delete()
    return redirect("adminpanel:brands")

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model

from .forms import JobVacancyForm, PartForm
from .models import JobVacancy, Part, WorkList

from django.shortcuts import redirect

from .models import InventoryCategory, Brand

def admin_login(request):
    """Admin login view that checks for staff/superuser status"""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect("dashboard")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            if not (user.is_staff or user.is_superuser):
                messages.error(request, "Access denied. Admin privileges required.")
                return render(request, "login.html")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "login.html")
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Access denied. Admin privileges required.")
        else:
            messages.error(request, "Invalid email or password.")
        
        return render(request, "login.html")
    
    return render(request, "login.html")


def is_admin(user):
    # adjust if you have your own role field
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    # Inventory stats
    total_items = Part.objects.count()
    low_stock_items = Part.objects.filter(quantity__gt=0, quantity__lte=F("min_stock_level")).count()
    out_of_stock_items = Part.objects.filter(quantity=0).count()

    # Recent inventory for table
    recent_inventory = Part.objects.all().order_by("-created_at")[:5]

    # Jobs stats (WorkList)
    total_jobs = WorkList.objects.count()
    pending_jobs = WorkList.objects.filter(job_status="assigned").count()
    in_progress_jobs = WorkList.objects.filter(job_status="in_progress").count()

    recent_jobs = WorkList.objects.select_related("user", "appointment").order_by("-created_at")[:5]

    # Customers stats (if you have Customer model later, replace this)
    # For now we count non-staff users as customers
    from django.contrib.auth import get_user_model
    User = get_user_model()

    total_customers = User.objects.filter(is_staff=False, is_superuser=False).count()

    today = timezone.localdate()
    new_customers_today = User.objects.filter(
        is_staff=False, is_superuser=False,
        date_joined__date=today
    ).count()

    # Appointments stats (you can replace later)
    pending_appointments = 0

    context = {
        "page_title": "Dashboard",
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "recent_inventory": recent_inventory,
        "total_jobs": total_jobs,
        "recent_jobs": recent_jobs,
        "total_customers": total_customers,
        "new_customers_today": new_customers_today,
        "pending_jobs": pending_jobs,
        "in_progress_jobs": in_progress_jobs,
        "pending_appointments": pending_appointments,
    }
    return render(request, "adminpanel/dashboard.html", context)


# -------- Inventory (needed for your dashboard links) --------
@login_required
@user_passes_test(is_admin)
def inventory(request):
    search_query = request.GET.get("search", "").strip()
    qs = Part.objects.select_related("category", "brand").all()

    if search_query:
            qs = qs.filter(
        Q(name__icontains=search_query) |
        Q(compatible_model__icontains=search_query) |
        Q(category__category_name__icontains=search_query) |
        Q(brand__brand_name__icontains=search_query)
    )

    out_of_stock_items = qs.filter(quantity=0).count()

    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page")
    inventory_items = paginator.get_page(page_number)

    return render(
        request,
        "adminpanel/inventory.html",
        {
            "page_title": "Inventory",
            "inventory_items": inventory_items,
            "search_query": search_query,
            "out_of_stock_items": out_of_stock_items,
        },
    )


@login_required
@user_passes_test(is_admin)
def add_inventory_item(request):
    if request.method == "POST":
        form = PartForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:inventory")
    else:
        form = PartForm()

    return render(request, "adminpanel/add_inventory_item.html", {"page_title": "Inventory", "form": form})


@login_required
@user_passes_test(is_admin)
def edit_inventory_item(request, part_id):
    item = get_object_or_404(Part, part_id=part_id)

    if request.method == "POST":
        form = PartForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:inventory")
    else:
        form = PartForm(instance=item)

    return render(
        request,
        "adminpanel/edit_inventory_item.html",
        {"page_title": "Inventory", "form": form, "item": item},
    )


@login_required
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
def delete_inventory_item(request, part_id):
    item = get_object_or_404(Part, part_id=part_id)

    if request.method == "POST":
        item.delete()
        return redirect("adminpanel:inventory")  

    return render(
        request,
        "adminpanel/delete_inventory_item.html",
        {"page_title": "Inventory", "item": item},
    )


@login_required
@user_passes_test(is_admin)
def item_details(request, part_id):
    item = get_object_or_404(Part.objects.select_related("category", "brand"), part_id=part_id)
    return render(request, "adminpanel/item_details.html", {"page_title": "Inventory", "item": item})


# -------- Jobs (Vacancy) --------
@login_required
@user_passes_test(is_admin)
def jobs(request):
    vacancies = JobVacancy.objects.all()
    return render(request, "adminpanel/jobs.html", {"page_title": "Jobs", "vacancies": vacancies})


@login_required
@user_passes_test(is_admin)
def create_job(request):
    if request.method == "POST":
        form = JobVacancyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("adminpanel:jobs")
    else:
        form = JobVacancyForm()

    return render(
        request,
        "adminpanel/create_job.html",
        {"page_title": "Jobs", "form": form},
    )


# -------- Logout --------
@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    if request.method in ["POST", "GET"]:
        logout(request)
        return redirect("login")

# -------- Leaves (if you have staff branch merged) --------
try:
    from staff.models import LeaveApplication
except Exception:
    LeaveApplication = None
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@login_required
@user_passes_test(is_admin)
def leaves(request):
    if LeaveApplication is None:
        # staff branch not merged yet
        return render(
            request,
            "adminpanel/leaves_not_ready.html",
            {"page_title": "Leaves"},
        )

    leaves_qs = LeaveApplication.objects.select_related("user").order_by("-applied_at")
    return render(
        request,
        "adminpanel/leaves.html",
        {"page_title": "Leaves", "leaves": leaves_qs},
    )


@login_required
@user_passes_test(is_admin)
def decide_leave(request, leave_id, action):
    if LeaveApplication is None:
        return redirect("adminpanel:leaves")

    leave = get_object_or_404(LeaveApplication, leave_id=leave_id)

    if action == "approve":
        leave.status = "approved"
    elif action == "reject":
        leave.status = "rejected"
    else:
        return redirect("adminpanel:leaves")

    leave.decided_at = timezone.now()
    leave.save(update_fields=["status", "decided_at"])

    return redirect("adminpanel:leaves")


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

# ----------- Categories -----------
@login_required
@user_passes_test(is_admin)
def categories(request):
    categories = InventoryCategory.objects.all().order_by("category_name")
    return render(request, "adminpanel/categories.html", {
        "page_title": "Categories",
        "categories": categories,
    })

@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == "POST":
        name = (request.POST.get("category_name") or "").strip()
        if name:
            InventoryCategory.objects.get_or_create(category_name=name)
            return redirect("adminpanel:categories")

    return render(request, "adminpanel/add_category.html", {"page_title": "Categories"})

@login_required
@user_passes_test(is_admin)
def delete_category(request, category_id):
    category = get_object_or_404(InventoryCategory, category_id=category_id)
    category.delete()
    return redirect("adminpanel:categories")

# ----------- Brands -----------
@login_required
@user_passes_test(is_admin)
def brands(request):
    brands = Brand.objects.all().order_by("brand_name")
    return render(request, "adminpanel/brands.html", {
        "page_title": "Brands",
        "brands": brands,
    })

@login_required
@user_passes_test(is_admin)
def add_brand(request):
    if request.method == "POST":
        name = (request.POST.get("brand_name") or "").strip()
        if name:
            Brand.objects.get_or_create(brand_name=name)
            return redirect("adminpanel:brands")

    return render(request, "adminpanel/add_brand.html", {"page_title": "Brands"})

@login_required
@user_passes_test(is_admin)
def delete_brand(request, brand_id):
    brand = get_object_or_404(Brand, brand_id=brand_id)
    brand.delete()
    return redirect("adminpanel:brands")