from django import forms
from .models import Part, JobVacancy


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
        }