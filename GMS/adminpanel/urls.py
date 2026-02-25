from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path("", views.admin_dashboard, name="dashboard"),
    path("calendar/", views.slot_calendar, name="slot_calendar"),
    path("add-slot/", views.add_slot, name="add_slot"),
    path("toggle-slot/<int:slot_id>/", views.toggle_slot_status, name="toggle_slot_status"),
]