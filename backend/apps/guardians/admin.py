from django.contrib import admin

from .models import Guardian


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ("guardian_id", "name", "phone", "created_at")
    search_fields = ("guardian_id", "name", "phone")
