from django.urls import path
from . import views
app_name = "adminpanel"

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

    # Logout
    path("logout/", views.admin_logout, name="admin_logout"),

    path("leaves/", views.leaves, name="leaves"),
    path("leaves/<int:leave_id>/<str:action>/", views.decide_leave, name="decide_leave"),

    path("categories/", views.categories, name="categories"),
    path("categories/add/", views.add_category, name="add_category"),
    path("categories/<int:category_id>/delete/", views.delete_category, name="delete_category"),

    path("brands/", views.brands, name="brands"),
    path("brands/add/", views.add_brand, name="add_brand"),
    path("brands/<int:brand_id>/delete/", views.delete_brand, name="delete_brand"),
]