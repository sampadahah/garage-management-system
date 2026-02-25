from django.db import models
from django.conf import settings

class Slot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]
        unique_together = ("date", "start_time", "end_time")

    def __str__(self):
        status = "Booked" if self.is_booked else "Available"
        return f"{self.date} {self.start_time}-{self.end_time} ({status})"