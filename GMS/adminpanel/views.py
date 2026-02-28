from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date, datetime, timedelta
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from .utils import render_to_pdf
from .models import Slot, Service
from .forms import SlotForm, ServiceForm, AdminUserCreateForm
from .forms import JobVacancyForm, PartForm
from .models import JobVacancy, Part
from .models import InventoryCategory, Brand

from customer.models import Appointment





Users=get_user_model()

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

@login_required
@user_passes_test(is_admin)
def create_user(request):

    if request.method == "POST":
        form = AdminUserCreateForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])

            # If Admin role selected
            if user.role == "Admin":
                user.is_superuser = True
                user.is_staff = True

            user.save()

            messages.success(request, "User created successfully.")
            return redirect("adminpanel:users_list")

    else:
        form = AdminUserCreateForm()

    return render(request, "adminpanel/create_user.html", {
        "form": form
    })

@login_required
@user_passes_test(is_admin)
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
@user_passes_test(is_admin)
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
@user_passes_test(is_admin)
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
@user_passes_test(is_admin)
# def customers(request):
#     """View all customers"""
#     from django.contrib.auth import get_user_model
#     User = get_user_model()
    
#     # Get all customers (non-staff users)
#     customers_list = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
    
#     context = {
#         'customers': customers_list,
#         'total_customers': customers_list.count(),
#     }
#     return render(request, "adminpanel/customers.html", context)
def users_list(request):
    role_filter = request.GET.get("role")

    users = Users.objects.all().order_by("-id")

    if role_filter:
        users = users.filter(role=role_filter)

    return render(request, "adminpanel/user_list.html", {
        "users": users,
        "role_filter": role_filter
    })

@login_required
@user_passes_test(is_admin)
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
@user_passes_test(is_admin)
def reports(request):
    User = get_user_model()

    total_slots = Slot.objects.count()
    booked_slots = Slot.objects.filter(is_booked=True).count()
    available_slots = total_slots - booked_slots

    total_customers = User.objects.filter(role="Customer").count()
    total_mechanics = User.objects.filter(role="Mechanic").count()

    total_appointments = Appointment.objects.count()

    appointment_status = Appointment.objects.aggregate(
        pending=Count("id", filter=Q(status="Pending")),
        confirmed=Count("id", filter=Q(status="Confirmed")),
        completed=Count("id", filter=Q(status="Completed")),
        cancelled=Count("id", filter=Q(status="Cancelled")),
    )

    utilization = (booked_slots / total_slots * 100) if total_slots else 0

    context = {
        "total_slots": total_slots,
        "booked_slots": booked_slots,
        "available_slots": available_slots,
        "utilization": round(utilization, 2),
        "total_customers": total_customers,
        "total_mechanics": total_mechanics,
        "total_appointments": total_appointments,
        "appointment_status": appointment_status,
    }
    return render(request, "adminpanel/reports.html", context)


@login_required
@user_passes_test(is_admin)
def download_slots_report_pdf(request):
    slots = Slot.objects.all().order_by("-date", "start_time")
    context = {"title": "Slots Report", "slots": slots}
    return render_to_pdf("adminpanel/pdf/slots_report_pdf.html", context, filename="slots_report.pdf")


@login_required
@user_passes_test(is_admin)
def download_customers_report_pdf(request):
    User = get_user_model()
    customers = User.objects.filter(role="Customer").order_by("name")
    context = {"title": "Customers Report", "customers": customers}
    return render_to_pdf("adminpanel/pdf/customers_report_pdf.html", context, filename="customers_report.pdf")


@login_required
@user_passes_test(is_admin)
def download_appointments_report_pdf(request):
    appointments = Appointment.objects.select_related("user", "vehicle", "slot").order_by("-created_at")
    context = {"title": "Appointments Report", "appointments": appointments}
    return render_to_pdf(
        "adminpanel/pdf/appointments_report_pdf.html",
        context,
        filename="appointments_report.pdf",
    )



def admin_service_list(request):
    services = Service.objects.all()
    return render(request, 'adminpanel/service_list.html', {'services': services})

def admin_add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminpanel:admin_service_list')
    else:
        form = ServiceForm()
    return render(request, 'adminpanel/service_form.html', {'form': form, 'title': 'Add Service'})

def admin_edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('adminpanel:admin_service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'adminpanel/service_form.html', {'form': form, 'title': 'Edit Service'})

def admin_delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('adminpanel:admin_service_list')
    return render(request, 'adminpanel/service_confirm_delete.html', {'service': service})

def is_admin(user):
    # adjust if you have your own role field
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Inventory stats
    total_items = Part.objects.count()
    low_stock_items = Part.objects.filter(quantity__gt=0, quantity__lte=F("min_stock_level")).count()
    out_of_stock_items = Part.objects.filter(quantity=0).count()

    # Recent inventory for table
    recent_inventory = Part.objects.all().order_by("-created_at")[:5]

    # Jobs stats (WorkList)
    # total_jobs = WorkList.objects.count()
    # pending_jobs = WorkList.objects.filter(job_status="assigned").count()
    # in_progress_jobs = WorkList.objects.filter(job_status="in_progress").count()

    # recent_jobs = WorkList.objects.select_related("user", "appointment").order_by("-created_at")[:5]

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
        # "total_jobs": total_jobs,
        # "recent_jobs": recent_jobs,
        "total_customers": total_customers,
        "new_customers_today": new_customers_today,
        # "pending_jobs": pending_jobs,
        # "in_progress_jobs": in_progress_jobs,
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
            obj = form.save(commit=False)
            obj.category = "mechanic"   # ✅ force mechanic only
            obj.save()
            messages.success(request, "Mechanic vacancy posted successfully.")
            return redirect("adminpanel:jobs")
    else:
        form = JobVacancyForm()

    return render(request, "adminpanel/create_job.html", {"form": form})


# -------- Leaves (if you have staff branch merged) --------
# try:
#     from staff.models import LeaveApplication
# except Exception:
#     LeaveApplication = None


# @login_required
# @user_passes_test(is_admin)
# def leaves(request):
#     if LeaveApplication is None:
#         # staff branch not merged yet
#         return render(
#             request,
#             "adminpanel/leaves_not_ready.html",
#             {"page_title": "Leaves"},
#         )

#     leaves_qs = LeaveApplication.objects.select_related("user").order_by("-applied_at")
#     return render(
#         request,
#         "adminpanel/leaves.html",
#         {"page_title": "Leaves", "leaves": leaves_qs},
#     )


# @login_required
# @user_passes_test(is_admin)
# def decide_leave(request, leave_id, action):
#     if LeaveApplication is None:
#         return redirect("adminpanel:leaves")

#     leave = get_object_or_404(LeaveApplication, leave_id=leave_id)

#     if action == "approve":
#         leave.status = "approved"
#     elif action == "reject":
#         leave.status = "rejected"
#     else:
#         return redirect("adminpanel:leaves")

#     leave.decided_at = timezone.now()
#     leave.save(update_fields=["status", "decided_at"])

#     return redirect("adminpanel:leaves")


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



from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


from customer.models import Appointment   
from django.contrib.auth import get_user_model

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def appointments_list(request):
    appointments = (
        Appointment.objects
        .select_related("user", "vehicle", "slot")
        .order_by("-created_at") 
    )
    return render(request, "adminpanel/appointments.html", {"appointments": appointments})


@login_required
@user_passes_test(is_admin)
def assign_mechanic(request, appointment_id):
    appt = get_object_or_404(Appointment, pk=appointment_id)

    # get all mechanics (based on your user.role)
    mechanics = User.objects.filter(role__iexact="Mechanic", is_active=True)

    if request.method == "POST":
        mechanic_id = request.POST.get("mechanic_id")

        if not mechanic_id:
            messages.error(request, "Please select a mechanic.")
            return redirect("adminpanel:assign_mechanic", appointment_id=appointment_id)

        mechanic = get_object_or_404(mechanics, pk=mechanic_id)

        # assign mechanic
        appt.mechanic = mechanic          # make sure Appointment has mechanic FK
        appt.status = "assigned"          # optional: if you have status field
        appt.save()

        messages.success(request, f"Mechanic assigned: {mechanic.get_full_name() or mechanic.username}")
        return redirect("adminpanel:appointments")

    return render(request, "adminpanel/assign_mechanic.html", {
        "appt": appt,
        "mechanics": mechanics
    })