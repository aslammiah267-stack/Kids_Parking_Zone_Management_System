from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .fees import calculate_parking_fee
from .models import ParkingRecord, ParkingSlot


def get_active_record(vehicle):
    return (
        ParkingRecord.objects.select_related("slot", "vehicle")
        .filter(vehicle=vehicle, status__in=[ParkingRecord.Status.RESERVED, ParkingRecord.Status.ACTIVE])
        .first()
    )


@transaction.atomic
def park_vehicle(vehicle, slot):
    slot = ParkingSlot.objects.select_for_update().get(pk=slot.pk)
    if slot.status == ParkingSlot.Status.OCCUPIED:
        raise ValidationError(f"{slot.slot_id} is already occupied.")
    if get_active_record(vehicle):
        raise ValidationError(f"Vehicle {vehicle.vehicle_id} is already parked.")

    slot.status = ParkingSlot.Status.OCCUPIED
    slot.save(update_fields=["status"])
    record = ParkingRecord.objects.create(
        vehicle=vehicle,
        slot=slot,
        status=ParkingRecord.Status.RESERVED,
    )
    return record


@transaction.atomic
def process_entry(vehicle, slot=None):
    record = get_active_record(vehicle)
    if record and record.status == ParkingRecord.Status.ACTIVE:
        raise ValidationError(f"Vehicle {vehicle.vehicle_id} is already inside the zone.")
    if record and record.status == ParkingRecord.Status.RESERVED:
        record.status = ParkingRecord.Status.ACTIVE
        record.entry_time = timezone.now()
        record.save(update_fields=["status", "entry_time"])
        return record
    if slot is None:
        raise ValidationError(
            f"Vehicle {vehicle.vehicle_id} is not assigned to a slot. Use PARK first or provide a slot."
        )
    record = park_vehicle(vehicle, slot)
    record.status = ParkingRecord.Status.ACTIVE
    record.entry_time = timezone.now()
    record.save(update_fields=["status", "entry_time"])
    return record


@transaction.atomic
def process_exit(vehicle):
    record = (
        ParkingRecord.objects.select_for_update()
        .select_related("slot")
        .filter(vehicle=vehicle, status=ParkingRecord.Status.ACTIVE)
        .first()
    )
    if not record:
        reserved = get_active_record(vehicle)
        if reserved:
            raise ValidationError(
                f"Vehicle {vehicle.vehicle_id} is reserved but has not entered. Complete ENTRY first."
            )
        raise ValidationError(f"Vehicle {vehicle.vehicle_id} is not currently parked.")

    now = timezone.now()
    entry = record.entry_time or record.created_at
    duration = max(int((now - entry).total_seconds() // 60), 1)
    fee = calculate_parking_fee(duration)

    slot = ParkingSlot.objects.select_for_update().get(pk=record.slot_id)
    slot.status = ParkingSlot.Status.AVAILABLE
    slot.save(update_fields=["status"])

    record.exit_time = now
    record.duration_minutes = duration
    record.fee = fee
    record.status = ParkingRecord.Status.EXITED
    record.save()
    return record


def preview_duration_and_fee(record):
    if record.status == ParkingRecord.Status.ACTIVE:
        entry = record.entry_time or record.created_at
        duration = max(int((timezone.now() - entry).total_seconds() // 60), 1)
        return duration, calculate_parking_fee(duration)
    return record.duration_minutes, record.fee
