# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, get_user_model
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
                status="Active"
            )
            user.set_password(password1)
            user.save()
            login(request, user)  # auto login after signup
            messages.success(request, "Account created successfully!")
            return redirect("customer_dashboard")
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
            login(request, user)
            return redirect("customer_dashboard")  
        else:
            print("Invalid credentials")

    return render(request, "login.html")

@login_required
def customer_dashboard(request):
    return render(request, "dashboard.html")