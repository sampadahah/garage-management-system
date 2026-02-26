from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path("", views.admin_dashboard, name="dashboard"),
    path("calendar/", views.slot_calendar, name="slot_calendar"),
    path("add-slot/", views.add_slot, name="add_slot"),
    path("toggle-slot/<int:slot_id>/", views.toggle_slot_status, name="toggle_slot_status"),
    path("customers/", views.customers, name="customers"),
    path("reports/", views.reports, name="reports"),
    path("reports/download-slots/", views.download_slots_report, name="download_slots_report"),
    path("reports/download-customers/", views.download_customers_report, name="download_customers_report"),
    path("reports/download-bookings/", views.download_bookings_report, name="download_bookings_report"),
    path("reports/download-all/", views.download_all_reports, name="download_all_reports"),

    # List all services
    path('services/', views.admin_service_list, name='admin_service_list'),

    # Add a new service
    path('services/add/', views.admin_add_service, name='admin_add_service'),

    # Edit an existing service
    path('services/edit/<int:pk>/', views.admin_edit_service, name='admin_edit_service'),

    # Delete a service
    path('services/delete/<int:pk>/', views.admin_delete_service, name='admin_delete_service'),
]