from django.urls import path
from .views import *

urlpatterns = [
    path("signup/", customer_signup, name="signup"),
    path("dashboard/", customer_dashboard, name="customer_dashboard"),
    path("login/", login_view, name="login"),
]