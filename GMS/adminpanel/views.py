from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Slot
from .forms import SlotForm
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