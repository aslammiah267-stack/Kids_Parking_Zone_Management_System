from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.CharField(source="vehicle.vehicle_id", read_only=True)
    record_id = serializers.IntegerField(source="parking_record.record_id", read_only=True)
    duration_minutes = serializers.IntegerField(source="parking_record.duration_minutes", read_only=True)
    fee = serializers.DecimalField(
        source="parking_record.fee", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "payment_id",
            "vehicle",
            "vehicle_id",
            "parking_record",
            "record_id",
            "amount",
            "duration_minutes",
            "fee",
            "payment_time",
            "payment_status",
        )
        read_only_fields = (
            "payment_id",
            "payment_time",
            "vehicle_id",
            "record_id",
            "duration_minutes",
            "fee",
        )
