from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import *
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