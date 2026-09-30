from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("vehicle_id", "vehicle_type", "child", "created_at")
    search_fields = ("vehicle_id", "child__child_id")
