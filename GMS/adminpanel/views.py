from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model

from .forms import JobVacancyForm, PartForm
from .models import JobVacancy, Notification, Part, WorkList


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
        qs = qs.filter(name__icontains=search_query)

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
            return redirect("inventory")
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
            return redirect("inventory")
    else:
        form = PartForm(instance=item)

    return render(
        request,
        "adminpanel/edit_inventory_item.html",
        {"page_title": "Inventory", "form": form, "item": item},
    )


@login_required
@user_passes_test(is_admin)
def delete_inventory_item(request, part_id):
    item = get_object_or_404(Part, part_id=part_id)

    if request.method == "POST":
        item.delete()
        return redirect("inventory")

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
            return redirect("jobs")
    else:
        form = JobVacancyForm()

    return render(request, "adminpanel/create_job.html", {"page_title": "Jobs", "form": form})


# -------- Notifications --------
@login_required
@user_passes_test(is_admin)
def notifications(request):
    notifications_qs = Notification.objects.all()
    return render(
        request,
        "adminpanel/notifications.html",
        {"page_title": "Notifications", "notifications": notifications_qs},
    )


@login_required
@user_passes_test(is_admin)
def mark_notification_read(request, id):
    n = get_object_or_404(Notification, id=id)
    n.is_read = True
    n.save(update_fields=["is_read"])
    return redirect("notifications")


@login_required
@user_passes_test(is_admin)
def mark_all_notifications_read(request):
    Notification.objects.filter(is_read=False).update(is_read=True)
    return redirect("notifications")


# -------- Logout --------
@login_required
def admin_logout(request):
    logout(request)
    # change this to your login url name if different
    return redirect("admin_login")