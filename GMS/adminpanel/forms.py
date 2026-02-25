from django import forms
from django.contrib.auth import get_user_model
from .models import Part, WorkList, Vacancy

User = get_user_model()


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
        }


class WorkListForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(role="Mechanic"),
        required=True
    )

    class Meta:
        model = WorkList
        fields = ["user", "job_status", "estimated_time", "appointment", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ["category", "title", "openings", "deadline", "status", "description", "requirements"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
            "requirements": forms.Textarea(attrs={"rows": 5}),
        }