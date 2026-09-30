from django.db import models

from apps.vehicles.models import Vehicle


class ParkingSettings(models.Model):
    """Singleton-style configurable parking fee rules."""

    first_block_minutes = models.PositiveIntegerField(default=30)
    first_block_fee = models.DecimalField(max_digits=8, decimal_places=2, default=20)
    extra_block_minutes = models.PositiveIntegerField(default=30)
    extra_block_fee = models.DecimalField(max_digits=8, decimal_places=2, default=10)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Parking settings"

    def __str__(self):
        return "Parking fee settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ParkingSlot(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        OCCUPIED = "OCCUPIED", "Occupied"

    slot_id = models.CharField(max_length=32, primary_key=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slot_id"]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.slot_id} ({self.status})"


class ParkingRecord(models.Model):
    class Status(models.TextChoices):
        RESERVED = "RESERVED", "Reserved"
        ACTIVE = "ACTIVE", "Active"
        EXITED = "EXITED", "Exited"
        PAID = "PAID", "Paid"

    record_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="parking_records")
    slot = models.ForeignKey(ParkingSlot, on_delete=models.PROTECT, related_name="parking_records")
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RESERVED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["entry_time"]),
            models.Index(fields=["vehicle", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=models.Q(status__in=["RESERVED", "ACTIVE"]),
                name="one_active_parking_per_vehicle",
            ),
        ]

    def __str__(self):
        return f"PR{self.record_id} {self.vehicle_id} {self.status}"
