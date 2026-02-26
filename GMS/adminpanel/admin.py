from django.contrib import admin
from .models import InventoryCategory, Brand, Part

admin.site.register(InventoryCategory)
admin.site.register(Brand)
admin.site.register(Part)