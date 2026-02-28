from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import *
from adminpanel.models import Slot, Service
from django.utils.dateparse import parse_date

User = get_user_model()

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}),
    )

    class Meta:
        model = Users
        fields = ["name", "email", "phone", "address"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Full name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "address": forms.TextInput(attrs={"placeholder": "Address"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if Users.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")

        if p1:
            validate_password(p1)

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = user.email.lower().strip()
        user.role = "Customer"
        user.status = "Active"
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": "profile-input",
            "placeholder": "Enter new password"
        }),
        required=False
    )

    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            "class": "profile-input",
            "placeholder": "Confirm new password"
        }),
        required=False
    )

    class Meta:
        model = Users
        fields = ("name", "email", "phone", "address")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "Full Name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "profile-input",
                "placeholder": "Email Address"
            }),
            "phone": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "Phone Number"
            }),
            "address": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "Address"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")

        # Only validate if user is changing password
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords do not match.")
            validate_password(p1)

        return cleaned_data

class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicle
        fields = ["model", "year", "plate_no", "image"]
        widgets = {
            "model": forms.TextInput(attrs={"class": "profile-input"}),
            "year": forms.NumberInput(attrs={"class": "profile-input"}),
            "plate_no": forms.TextInput(attrs={"class": "profile-input"}),
            "image": forms.FileInput(attrs={"class": "profile-input"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_plate_no(self):
        plate = self.cleaned_data.get("plate_no")

        if plate:
            plate = plate.upper().strip()

            if self.user:
                exists = Vehicle.objects.filter(
                    user=self.user,
                    plate_no__iexact=plate
                ).exclude(pk=self.instance.pk).exists()

                if exists:
                    raise forms.ValidationError(
                        "You already have a vehicle registered with this plate number."
                    )

        return plate


class AppointmentCreateForm(forms.ModelForm):

    date = forms.DateField(
        input_formats=["%Y-%m-%d", "%m/%d/%Y"],
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True
    )

    class Meta:
        model = Appointment
        fields = ["vehicle", "service", "slot", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Write additional notes..."}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        service_id = kwargs.pop("service_id", None)  # ✅ ADD THIS
        super().__init__(*args, **kwargs)

        self.fields["vehicle"].widget.attrs["class"] = "form-select"
        self.fields["service"].widget.attrs["class"] = "form-select"
        self.fields["slot"].widget.attrs["class"] = "form-select"

        if user:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(user=user).order_by("-created_at")

        self.fields["vehicle"].empty_label = "Choose vehicle"
        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        self.fields["service"].empty_label = "Choose service"

        # ✅ SET DEFAULT SERVICE FROM BOOK NOW LINK (GET)
        if service_id:
            self.initial["service"] = service_id

        # slot default
        self.fields["slot"].queryset = Slot.objects.none()
        self.fields["slot"].empty_label = "Select time slot"

        # On POST rebuild slot queryset
        if self.data:
            date_val = self.data.get("date")
            service_id_post = self.data.get("service")  # available on POST

            date_obj = parse_date(date_val)
            if date_obj is None and date_val:
                from datetime import datetime
                try:
                    date_obj = datetime.strptime(date_val, "%m/%d/%Y").date()
                except ValueError:
                    date_obj = None

            if date_obj:
                qs = Slot.objects.filter(date=date_obj, is_booked=False).order_by("start_time")
                self.fields["slot"].queryset = qs