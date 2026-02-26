from django import forms
from .models import Slot, Service
from django.forms import DateInput, TimeInput

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