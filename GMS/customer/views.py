# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login, get_user_model
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

User = get_user_model()

def customer_signup(request):
    if request.method == "POST":
        # Get data from the plain HTML form fields
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        password1 = request.POST.get('password1', '')
        
        # Combine first and last name
        full_name = f"{first_name} {last_name}".strip()
        
        # Basic validation
        errors = []
        if not full_name:
            errors.append("Please enter your name.")
        if not email:
            errors.append("Please enter your email.")
        if not password1:
            errors.append("Please enter a password.")
        if len(password1) < 8:
            errors.append("Password must be at least 8 characters long.")
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            errors.append("This email is already registered.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "signup.html")
        
        # Create the user
        try:
            user = User(
                email=email,
                name=full_name,
                phone=phone,
                address=address,
                role="Customer",
                is_active=False,      #  must verify email first
                is_verified=False,
            )
            user.set_password(password1)
            user.save()

            verify_path = reverse("verify_email", args=[str(user.email_verification_token)])
            verify_link = request.build_absolute_uri(verify_path)

            subject = "Verify your email"
            message = (
                f"Hi {user.name},\n\n"
                f"Thanks for signing up.\n"
                f"Please verify your email by clicking the link below:\n\n"
                f"{verify_link}\n\n"
                f"If you did not create this account, you can ignore this email."
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "Account created! Please check your email to verify your account.")
            return redirect("login")

        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, "signup.html")

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Please verify your email first. Check your inbox.")
                return redirect("login")

            login(request, user)
            return redirect("customer_dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html")

def verify_email(request, token):
    user = get_object_or_404(User, email_verification_token=token)

    if not user.is_verified:
        user.is_verified = True
        user.is_active = True
        user.email_verification_token = None  # optional: invalidate token
        user.save()
        messages.success(request, "Email verified successfully! You can now log in.")
    else:
        messages.info(request, "Your email is already verified. Please log in.")

    return redirect("login")


@login_required
def customer_dashboard(request):
    return render(request, "dashboard.html")