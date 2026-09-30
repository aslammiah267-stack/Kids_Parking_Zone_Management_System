from rest_framework import serializers

from apps.payments.models import Payment
from .models import ParkingRecord, ParkingSettings, ParkingSlot
from .services import preview_duration_and_fee


class ParkingSlotSerializer(serializers.ModelSerializer):
    current_vehicle = serializers.SerializerMethodField()
    current_child = serializers.SerializerMethodField()
    current_guardian = serializers.SerializerMethodField()
    entry_time = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = ParkingSlot
        fields = (
            "slot_id",
            "status",
            "created_at",
            "current_vehicle",
            "current_child",
            "current_guardian",
            "entry_time",
            "duration_minutes",
        )
        read_only_fields = ("created_at",)

    def _active(self, obj):
        return (
            obj.parking_records.filter(status__in=["RESERVED", "ACTIVE"])
            .select_related("vehicle", "vehicle__child", "vehicle__child__guardian")
            .first()
        )

    def get_current_vehicle(self, obj):
        rec = self._active(obj)
        return rec.vehicle.vehicle_id if rec else None

    def get_current_child(self, obj):
        rec = self._active(obj)
        if not rec:
            return None
        child = rec.vehicle.child
        return {"child_id": child.child_id, "name": child.name}

    def get_current_guardian(self, obj):
        rec = self._active(obj)
        if not rec:
            return None
        g = rec.vehicle.child.guardian
        return {"guardian_id": g.guardian_id, "name": g.name, "phone": g.phone}

    def get_entry_time(self, obj):
        rec = self._active(obj)
        return rec.entry_time if rec else None

    def get_duration_minutes(self, obj):
        rec = self._active(obj)
        if not rec:
            return None
        duration, _ = preview_duration_and_fee(rec)
        return duration


class ParkingRecordSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.CharField(source="vehicle.vehicle_id", read_only=True)
    child_id = serializers.CharField(source="vehicle.child.child_id", read_only=True)
    child_name = serializers.CharField(source="vehicle.child.name", read_only=True)
    slot_id = serializers.CharField(source="slot.slot_id", read_only=True)
    payment_status = serializers.SerializerMethodField()
    live_duration_minutes = serializers.SerializerMethodField()
    live_fee = serializers.SerializerMethodField()

    class Meta:
        model = ParkingRecord
        fields = (
            "record_id",
            "vehicle",
            "vehicle_id",
            "child_id",
            "child_name",
            "slot",
            "slot_id",
            "entry_time",
            "exit_time",
            "duration_minutes",
            "fee",
            "status",
            "created_at",
            "payment_status",
            "live_duration_minutes",
            "live_fee",
        )
        read_only_fields = fields

    def get_payment_status(self, obj):
        payment = obj.payments.order_by("-payment_time").first()
        if payment:
            return payment.payment_status
        if obj.status == ParkingRecord.Status.PAID:
            return Payment.Status.COMPLETED
        if obj.status in (ParkingRecord.Status.EXITED,):
            return Payment.Status.PENDING
        return None

    def get_live_duration_minutes(self, obj):
        duration, _ = preview_duration_and_fee(obj)
        return duration

    def get_live_fee(self, obj):
        _, fee = preview_duration_and_fee(obj)
        return fee


class ParkingSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSettings
        fields = (
            "first_block_minutes",
            "first_block_fee",
            "extra_block_minutes",
            "extra_block_fee",
            "updated_at",
        )
        read_only_fields = ("updated_at",)
