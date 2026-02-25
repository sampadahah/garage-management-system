from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PartForm, WorkListForm
from .models import Part, WorkList
from .models import Vacancy
from .forms import VacancyForm
from django.contrib.auth import logout


def is_admin(user):
    return user.is_authenticated and getattr(user, "role", "") == "Admin"


admin_required = user_passes_test(is_admin, login_url="login")


User = get_user_model()


@admin_required
def dashboard(request):
    total_items = Part.objects.count()
    low_stock_items = Part.objects.filter(quantity__gt=0, quantity__lte=F("min_stock_level")).count()
    out_of_stock_items = Part.objects.filter(quantity=0).count()

    total_jobs = WorkList.objects.exclude(job_status="completed").count()

    recent_inventory = Part.objects.order_by("-created_at")[:5]
    recent_jobs = WorkList.objects.select_related(
        "user", "appointment", "appointment__service_package"
    ).order_by("-created_at")[:5]

    total_customers = User.objects.filter(role="Customer").count()
    new_customers_today = 0

    pending_jobs = WorkList.objects.filter(job_status="assigned").count()
    in_progress_jobs = WorkList.objects.filter(job_status="in_progress").count()
    pending_appointments = 0

    total_vacancies = Vacancy.objects.count()
    open_vacancies = Vacancy.objects.filter(status="open").count()
    closed_vacancies = Vacancy.objects.filter(status="closed").count()
    recent_vacancies = Vacancy.objects.order_by("-created_at")[:5]

    return render(request, "adminpanel/dashboard.html", {
        "page_title": "Dashboard",
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "total_jobs": total_jobs,
        "recent_inventory": recent_inventory,
        "recent_jobs": recent_jobs,
        "total_customers": total_customers,
        "new_customers_today": new_customers_today,
        "pending_jobs": pending_jobs,
        "in_progress_jobs": in_progress_jobs,
        "pending_appointments": pending_appointments,

        "total_vacancies": total_vacancies,
        "open_vacancies": open_vacancies,
        "closed_vacancies": closed_vacancies,
        "recent_vacancies": recent_vacancies,
    })

@admin_required
def inventory(request):
    search_query = request.GET.get("search", "").strip()

    qs = Part.objects.select_related("category", "brand").order_by("-created_at")

    if search_query:
        qs = qs.filter(
            Q(name__icontains=search_query) |
            Q(compatible_model__icontains=search_query) |
            Q(category__category_name__icontains=search_query) |
            Q(brand__brand_name__icontains=search_query)
        )

    paginator = Paginator(qs, 10)
    inventory_items = paginator.get_page(request.GET.get("page"))

    out_of_stock_items = Part.objects.filter(quantity=0).count()

    return render(request, "adminpanel/inventory.html", {
        "page_title": "Inventory",
        "inventory_items": inventory_items,
        "search_query": search_query,
        "out_of_stock_items": out_of_stock_items,
    })


@admin_required
def item_details(request, part_id):
    item = get_object_or_404(Part, part_id=part_id)
    return render(request, "adminpanel/item_details.html", {
        "page_title": "Inventory",
        "item": item,
    })


@admin_required
def add_inventory_item(request):
    if request.method == "POST":
        form = PartForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("inventory")
    else:
        form = PartForm()

    return render(request, "adminpanel/add_inventory_item.html", {
        "page_title": "Inventory",
        "form": form,
    })


@admin_required
def edit_inventory_item(request, part_id):
    item = get_object_or_404(Part, part_id=part_id)

    if request.method == "POST":
        form = PartForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("inventory")
    else:
        form = PartForm(instance=item)

    return render(request, "adminpanel/edit_inventory_item.html", {
        "page_title": "Inventory",
        "form": form,
        "item": item,
    })


@admin_required
def delete_inventory_item(request, part_id):
    item = get_object_or_404(Part, part_id=part_id)

    if request.method == "POST":
        item.delete()
        return redirect("inventory")

    return render(request, "adminpanel/delete_inventory_item.html", {
        "page_title": "Inventory",
        "item": item,
    })


@admin_required
def jobs(request):
    vacancies = Vacancy.objects.all()
    return render(request, "adminpanel/jobs.html", {
        "page_title": "Hiring",
        "vacancies": vacancies,
    })


@admin_required
def create_job(request):
    if request.method == "POST":
        form = VacancyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("jobs")
    else:
        form = VacancyForm()

    return render(request, "adminpanel/create_job.html", {
        "page_title": "Hiring",
        "form": form,
    })

@admin_required
def admin_logout(request):
    logout(request)
    return redirect("login")


@admin_required
def customers(request):
    return render(request, "adminpanel/coming_soon.html", {
        "page_title": "Customers"
    })


@admin_required
def appointments(request):
    return render(request, "adminpanel/coming_soon.html", {
        "page_title": "Bookings"
    })


@admin_required
def reports(request):
    return render(request, "adminpanel/coming_soon.html", {
        "page_title": "Reports"
    })


@admin_required
def staff(request):
    return render(request, "adminpanel/coming_soon.html", {
        "page_title": "Staff"
    })

