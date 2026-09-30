from django.contrib import admin

from .models import ParkingRecord, ParkingSettings, ParkingSlot


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ("slot_id", "status", "created_at")


@admin.register(ParkingRecord)
class ParkingRecordAdmin(admin.ModelAdmin):
    list_display = ("record_id", "vehicle", "slot", "status", "entry_time", "exit_time", "fee")


@admin.register(ParkingSettings)
class ParkingSettingsAdmin(admin.ModelAdmin):
    list_display = ("first_block_minutes", "first_block_fee", "extra_block_minutes", "extra_block_fee")
