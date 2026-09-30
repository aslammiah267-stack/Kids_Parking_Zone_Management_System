from django.db import models

from apps.parking.models import ParkingRecord
from apps.vehicles.models import Vehicle


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"

    payment_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="payments")
    parking_record = models.ForeignKey(ParkingRecord, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_time = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["-payment_time"]
        indexes = [models.Index(fields=["payment_status"]), models.Index(fields=["vehicle"])]

    def __str__(self):
        return f"PAY{self.payment_id} {self.amount} {self.payment_status}"
