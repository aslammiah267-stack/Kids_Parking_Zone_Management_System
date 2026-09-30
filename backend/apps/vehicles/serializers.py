from rest_framework import serializers

from apps.parking.models import ParkingRecord
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)
    guardian_id = serializers.CharField(source="child.guardian.guardian_id", read_only=True)
    guardian_name = serializers.CharField(source="child.guardian.name", read_only=True)
    status = serializers.SerializerMethodField()
    current_slot = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = (
            "vehicle_id",
            "vehicle_type",
            "child",
            "child_name",
            "guardian_id",
            "guardian_name",
            "status",
            "current_slot",
            "created_at",
        )
        read_only_fields = (
            "created_at",
            "child_name",
            "guardian_id",
            "guardian_name",
            "status",
            "current_slot",
        )

    def _active_record(self, obj):
        return (
            ParkingRecord.objects.filter(
                vehicle=obj,
                status__in=[
                    ParkingRecord.Status.RESERVED,
                    ParkingRecord.Status.ACTIVE,
                ],
            )
            .select_related("slot")
            .first()
        )

    def get_status(self, obj):
        record = self._active_record(obj)
        if not record:
            return "OUT"
        return record.status

    def get_current_slot(self, obj):
        record = self._active_record(obj)
        return record.slot.slot_id if record else None
