from django.test import TestCase

from apps.children.models import Child
from apps.compiler.errors import SemanticError
from apps.compiler.lexer import tokenize
from apps.compiler.parser import parse
from apps.compiler.semantic import analyze
from apps.guardians.models import Guardian
from apps.parking.models import ParkingRecord, ParkingSlot
from apps.vehicles.models import Vehicle


class SemanticTests(TestCase):
    def setUp(self):
        self.guardian = Guardian.objects.create(guardian_id="GUARD01", name="Test Guardian", phone="01700000000")
        self.child = Child.objects.create(child_id="CHILD101", name="Ayaan", age=6, guardian=self.guardian)
        self.vehicle = Vehicle.objects.create(vehicle_id="CAR101", vehicle_type="CAR", child=self.child)
        self.slot = ParkingSlot.objects.create(slot_id="SLOT05", status=ParkingSlot.Status.AVAILABLE)

    def _analyze(self, command):
        return analyze(parse(tokenize(command)))

    def test_unregistered_vehicle(self):
        with self.assertRaises(SemanticError) as ctx:
            self._analyze("PARK CAR999 SLOT05")
        self.assertIn("not registered", ctx.exception.message)

    def test_occupied_slot(self):
        self.slot.status = ParkingSlot.Status.OCCUPIED
        self.slot.save()
        with self.assertRaises(SemanticError) as ctx:
            self._analyze("PARK CAR101 SLOT05")
        self.assertIn("occupied", ctx.exception.message)

    def test_unknown_slot(self):
        with self.assertRaises(SemanticError) as ctx:
            self._analyze("PARK CAR101 SLOT99")
        self.assertIn("does not exist", ctx.exception.message)

    def test_vehicle_already_parked(self):
        ParkingRecord.objects.create(
            vehicle=self.vehicle, slot=self.slot, status=ParkingRecord.Status.RESERVED
        )
        self.slot.status = ParkingSlot.Status.OCCUPIED
        self.slot.save()
        other = ParkingSlot.objects.create(slot_id="SLOT06")
        with self.assertRaises(SemanticError) as ctx:
            self._analyze("PARK CAR101 SLOT06")
        self.assertIn("already parked", ctx.exception.message)
        other.slot_id  # keep slot used

    def test_exit_when_not_parked(self):
        with self.assertRaises(SemanticError) as ctx:
            self._analyze("EXIT CAR101")
        self.assertIn("not currently parked", ctx.exception.message)

    def test_invalid_payment(self):
        with self.assertRaises(SemanticError) as ctx:
            self._analyze("PAY CAR101")
        self.assertIn("Payment", ctx.exception.message)
