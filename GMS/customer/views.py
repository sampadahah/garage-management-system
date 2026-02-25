# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login, get_user_model, logout, update_session_auth_hash
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

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

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            verify_path = reverse("verify_email", kwargs={"uidb64": uidb64, "token": token})
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

        try:
            u = User.objects.get(email=email)
            if not u.is_active:
                messages.error(request, "Please verify your email first. Check your inbox.")
                return render(request, "login.html")
        except User.DoesNotExist:
            pass

        user = authenticate(request, username=email, password=password)
        
        # If authentication fails, try manual verification for email-based users
        if user is None:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    # Password is correct, use this user
                    pass
                else:
                    user = None
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect("customer_dashboard")
        
        messages.error(request, "Invalid email or password.")
        return render(request, "login.html")
        
    return render(request, "login.html")

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_verified:
            user.is_verified = True
            user.is_active = True
            user.save()
            messages.success(request, "Email verified successfully! You can now log in.")
        else:
            messages.info(request, "Your email is already verified. Please log in.")
    else:
        messages.error(request, "Verification link is invalid or expired.")

    return redirect("login")


@login_required
def customer_dashboard(request):
    vehicles = Vehicle.objects.filter(user=request.user)

    return render(request, "dashboard.html", {
        "vehicles": vehicles
    })

@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)

            new_password = form.cleaned_data.get("new_password1")
            if new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)
                messages.success(request, "Profile and password updated successfully!")
            else:
                messages.success(request, "Profile updated successfully!")

            user.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=user)

    return render(request, "profile.html", {"form": form})


@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(user=request.user)
    return render(request, "vehicle_list.html", {
        "vehicles": vehicles
    })


@login_required
def vehicle_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.user = request.user
            vehicle.save()
            messages.success(request, "Vehicle added successfully!")
            return redirect("vehicle_list")
        else: 
            # Show form errors using messages framework
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, error)
    else:
        form = VehicleForm()

    return render(request, "vehicle_form.html", {
        "form": form,
        "title": "Add Vehicle"
    })


@login_required
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)

    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES, instance=vehicle, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated successfully!")
            return redirect("vehicle_list")
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, "vehicle_form.html", {
        "form": form,
        "vehicle": vehicle,
        "title": "Edit Vehicle"
    })


@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)

    if request.method == "POST":
        vehicle.delete()
        messages.success(request, "Vehicle deleted!")
        return redirect("vehicle_list")

    return render(request, "vehicle_confirm_delete.html", {
        "vehicle": vehicle
    })

@login_required
def create_appointment(request):
    if request.method == "POST":
        form = AppointmentCreateForm(request.POST, user=request.user)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.user = request.user
            appt.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect("create_appointment") 
    else:
        form = AppointmentCreateForm(user=request.user)

    return render(request, "create_appointment.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")