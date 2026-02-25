from django.contrib import admin
from .models import Slot

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("date", "start_time", "end_time", "is_booked", "created_by", "created_at")
    list_filter = ("date", "is_booked")
    ordering = ("date", "start_time")