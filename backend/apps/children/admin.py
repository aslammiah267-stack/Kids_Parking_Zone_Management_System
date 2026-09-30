from django.contrib import admin

from .models import Child


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("child_id", "name", "age", "guardian", "created_at")
    search_fields = ("child_id", "name")
