from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # Inventory
    path("inventory/", views.inventory, name="inventory"),
    path("inventory/add/", views.add_inventory_item, name="add_inventory_item"),
    path("inventory/<int:part_id>/edit/", views.edit_inventory_item, name="edit_inventory_item"),
    path("inventory/<int:part_id>/delete/", views.delete_inventory_item, name="delete_inventory_item"),
    path("inventory/<int:part_id>/", views.item_details, name="item_details"),

    # Jobs
    path("jobs/", views.jobs, name="jobs"),
    path("jobs/create/", views.create_job, name="create_job"),

    # Notifications
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/<int:id>/read/", views.mark_notification_read, name="mark_notification_read"),
    path("notifications/read-all/", views.mark_all_notifications_read, name="mark_all_notifications_read"),

    # Logout
    path("logout/", views.admin_logout, name="admin_logout"),
]