from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("inventory/", views.inventory, name="inventory"),
    path("inventory/add/", views.add_inventory_item, name="add_inventory_item"),
    path("inventory/<int:part_id>/", views.item_details, name="item_details"),
    path("inventory/<int:part_id>/edit/", views.edit_inventory_item, name="edit_inventory_item"),
    path("inventory/<int:part_id>/delete/", views.delete_inventory_item, name="delete_inventory_item"),

    path("jobs/", views.jobs, name="jobs"),
    path("jobs/create/", views.create_job, name="create_job"),

   
    path("customers/", views.customers, name="customers"),
    path("appointments/", views.appointments, name="appointments"),
    path("reports/", views.reports, name="reports"),
    path("staff/", views.staff, name="staff"),
    path("logout/", views.admin_logout, name="admin_logout"),
]