from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.parking.models import ParkingRecord
from .models import Payment


@transaction.atomic
def collect_payment(vehicle, parking_record=None):
    if parking_record is None:
        parking_record = (
            ParkingRecord.objects.select_for_update()
            .filter(vehicle=vehicle, status=ParkingRecord.Status.EXITED)
            .order_by("-exit_time")
            .first()
        )
    if parking_record is None:
        raise ValidationError(
            f"No payable parking record for {vehicle.vehicle_id}. Exit the vehicle first."
        )
    if parking_record.vehicle_id != vehicle.vehicle_id:
        raise ValidationError("Payment vehicle does not match parking record.")
    if parking_record.status == ParkingRecord.Status.PAID:
        raise ValidationError("This parking record is already paid.")
    if parking_record.status != ParkingRecord.Status.EXITED:
        raise ValidationError("Payment is only allowed after a completed exit.")
    if parking_record.fee is None:
        raise ValidationError("Fee has not been calculated for this record.")

    existing = parking_record.payments.filter(payment_status=Payment.Status.COMPLETED).exists()
    if existing:
        raise ValidationError("Payment already completed for this record.")

    payment = Payment.objects.create(
        vehicle=vehicle,
        parking_record=parking_record,
        amount=parking_record.fee,
        payment_status=Payment.Status.COMPLETED,
    )
    parking_record.status = ParkingRecord.Status.PAID
    parking_record.save(update_fields=["status"])
    return payment
