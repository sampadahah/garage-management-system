from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path("vacancies/",vacancies_page, name="vacancies"),
    path("signup/", customer_signup, name="signup"),
    path("dashboard/", customer_dashboard, name="customer_dashboard"),
    path("login/", login_view, name="login"),
    path("verify-email/<uidb64>/<token>/", verify_email, name="verify_email"),

    path(
        "forgot-password/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html",
            email_template_name="password_reset_email.html",
            success_url="/customer/forgot-password/done/",
        ),
        name="password_reset",
    ),

    path(
        "forgot-password/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html",
            success_url="/customer/reset/done/",
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    path("profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),

    path("vehicles/", vehicle_list, name="vehicle_list"),
    path("vehicles/add/", vehicle_create, name="vehicle_add"),
    path("vehicles/<int:pk>/edit/", vehicle_update, name="vehicle_edit"),
    path("vehicles/<int:pk>/delete/", vehicle_delete, name="vehicle_delete"),

    path("appointments/", create_appointment, name="create_appointment"),
    path("appointments/available-slots/", available_slots, name="available_slots"),
]
