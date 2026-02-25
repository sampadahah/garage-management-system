from django import forms
from .models import Slot
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