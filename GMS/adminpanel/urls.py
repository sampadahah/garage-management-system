from django.urls import path
from .views import (inventory, add_inventory_item,edit_inventory_item,delete_inventory_item,item_details,
                    jobs,create_job,categories, add_category, delete_category,
                    brands, add_brand, delete_brand,
                    admin_dashboard, slot_calendar, add_slot,toggle_slot_status,
                    customers, reports, download_slots_report,download_customers_report,download_bookings_report,download_all_reports,
                    admin_service_list,admin_add_service,admin_delete_service,admin_edit_service)
app_name = "adminpanel"

urlpatterns = [

    # Dashboard
    # path("dashboard/", views.dashboard, name="dashboard"),

    # Inventory
    path("inventory/", inventory, name="inventory"),
    path("inventory/add/", add_inventory_item, name="add_inventory_item"),
    path("inventory/<int:part_id>/edit/", edit_inventory_item, name="edit_inventory_item"),
    path("inventory/<int:part_id>/delete/", delete_inventory_item, name="delete_inventory_item"),
    path("inventory/<int:part_id>/", item_details, name="item_details"),

    # Jobs
    path("jobs/", jobs, name="jobs"),
    path("jobs/create/", create_job, name="create_job"),

    # Logout
    # path("logout/", views.admin_logout, name="admin_logout"),

    # path("leaves/", views.leaves, name="leaves"),
    # path("leaves/<int:leave_id>/<str:action>/", views.decide_leave, name="decide_leave"),

    path("categories/", categories, name="categories"),
    path("categories/add/", add_category, name="add_category"),
    path("categories/<int:category_id>/delete/", delete_category, name="delete_category"),

    path("brands/", brands, name="brands"),
    path("brands/add/", add_brand, name="add_brand"),
    path("brands/<int:brand_id>/delete/", delete_brand, name="delete_brand"),

    path("", admin_dashboard, name="dashboard"),

    path("calendar/", slot_calendar, name="slot_calendar"),
    path("add-slot/", add_slot, name="add_slot"),
    path("toggle-slot/<int:slot_id>/", toggle_slot_status, name="toggle_slot_status"),
    path("customers/", customers, name="customers"),
    path("reports/", reports, name="reports"),
    path("reports/download-slots/", download_slots_report, name="download_slots_report"),
    path("reports/download-customers/", download_customers_report, name="download_customers_report"),
    path("reports/download-bookings/", download_bookings_report, name="download_bookings_report"),
    path("reports/download-all/", download_all_reports, name="download_all_reports"),

    # List all services
    path('services/', admin_service_list, name='admin_service_list'),
    path('services/add/', admin_add_service, name='admin_add_service'),
    path('services/edit/<int:pk>/', admin_edit_service, name='admin_edit_service'),
    path('services/delete/<int:pk>/', admin_delete_service, name='admin_delete_service'),
]