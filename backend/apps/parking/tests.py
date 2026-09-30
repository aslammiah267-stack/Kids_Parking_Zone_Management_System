from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.children.models import Child
from apps.guardians.models import Guardian
from apps.parking.fees import calculate_parking_fee
from apps.parking.models import ParkingRecord, ParkingSettings, ParkingSlot
from apps.parking.services import park_vehicle, process_entry, process_exit
from apps.payments.services import collect_payment
from apps.vehicles.models import Vehicle


class ParkingLogicTests(TestCase):
    def setUp(self):
        ParkingSettings.get_solo()
        guardian = Guardian.objects.create(guardian_id="GUARD01", name="G", phone="01700000000")
        child = Child.objects.create(child_id="CHILD001", name="Kid", age=5, guardian=guardian)
        self.vehicle = Vehicle.objects.create(vehicle_id="CAR001", vehicle_type="CAR", child=child)
        self.slot = ParkingSlot.objects.create(slot_id="SLOT01")

    def test_fee_calculation(self):
        self.assertEqual(calculate_parking_fee(30), 20)
        self.assertEqual(calculate_parking_fee(60), 30)
        self.assertEqual(calculate_parking_fee(90), 40)
        self.assertEqual(calculate_parking_fee(1), 20)

    def test_entry_exit_payment(self):
        park_vehicle(self.vehicle, self.slot)
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.status, ParkingSlot.Status.OCCUPIED)
        record = process_entry(self.vehicle)
        record.entry_time = timezone.now() - timedelta(minutes=60)
        record.save(update_fields=["entry_time"])
        exited = process_exit(self.vehicle)
        self.assertEqual(exited.fee, 30)
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.status, ParkingSlot.Status.AVAILABLE)
        payment = collect_payment(self.vehicle)
        self.assertEqual(payment.amount, exited.fee)
        exited.refresh_from_db()
        self.assertEqual(exited.status, ParkingRecord.Status.PAID)
