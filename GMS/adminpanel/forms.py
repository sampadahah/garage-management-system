from django import forms
from .models import Slot, Service, JobVacancy, Part
from django.forms import DateInput, TimeInput
from django.contrib.auth.password_validation import validate_password
from customer.models import Users


class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = ["date", "start_time", "end_time", "is_booked"]
        widgets = {
            "date": DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": TimeInput(attrs={"type": "time", "class": "form-control"}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

<<<<<<< HEAD
from django import forms
from .models import Part, JobVacancy


=======
>>>>>>> 76d74920ba13f72e930266cd6b1a3c34c0a441e3
class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = [
            "name",
            "compatible_model",
            "price",
            "quantity",
            "min_stock_level",
            "category",
            "brand",
            "image",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "requirements": forms.Textarea(attrs={"rows": 4}),
        }


class JobVacancyForm(forms.ModelForm):
    class Meta:
        model = JobVacancy
        fields = ["category", "title", "openings", "deadline", "description", "requirements", "status"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
            "requirements": forms.Textarea(attrs={"rows": 5}),
<<<<<<< HEAD
        }
=======
        }

class AdminUserCreateForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Users
        fields = ["name", "email", "phone", "address", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only allow Admin and Mechanic
        self.fields['role'].choices = [
            ('admin', 'Admin'),
            ('mechanic', 'Mechanic'),
        ]
    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 != p2:
            raise forms.ValidationError("Passwords do not match.")

        validate_password(p1)
        return cleaned
>>>>>>> 76d74920ba13f72e930266cd6b1a3c34c0a441e3
