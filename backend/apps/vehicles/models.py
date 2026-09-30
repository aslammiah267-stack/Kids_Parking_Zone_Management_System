from django.db import models

from apps.children.models import Child


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        CAR = "CAR", "Toy / Electric Car"
        BIKE = "BIKE", "Bike"
        TOY = "TOY", "Toy Vehicle"
        BUS = "BUS", "Mini Bus"
        OTHER = "OTHER", "Other"

    vehicle_id = models.CharField(max_length=32, primary_key=True)
    vehicle_type = models.CharField(max_length=16, choices=VehicleType.choices, default=VehicleType.CAR)
    child = models.ForeignKey(Child, on_delete=models.PROTECT, related_name="vehicles")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["vehicle_id"]
        indexes = [models.Index(fields=["vehicle_type"]), models.Index(fields=["child"])]

    def __str__(self):
        return f"{self.vehicle_id} ({self.vehicle_type})"
