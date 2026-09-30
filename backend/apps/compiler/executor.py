"""KPCL Executor.

Runs only after lexer, parser, and semantic analyzer succeed.
It maps intermediate instructions to Django database services.
"""

from apps.children.models import Child
from apps.guardians.models import Guardian
from apps.parking.models import ParkingSlot
from apps.parking.services import park_vehicle, process_entry, process_exit
from apps.payments.services import collect_payment
from apps.vehicles.models import Vehicle
from .tokens import TOKEN_CHILD_ID, TOKEN_GUARDIAN_ID, TOKEN_SLOT_ID, TOKEN_VEHICLE_ID


class Executor:
    def execute(self, ast):
        command_type = ast["type"]
        if command_type == "REGISTER_COMMAND":
            return self._register(ast)
        if command_type == "PARK_COMMAND":
            return self._park(ast)
        if command_type == "ENTRY_COMMAND":
            return self._entry(ast)
        if command_type == "EXIT_COMMAND":
            return self._exit(ast)
        if command_type == "PAY_COMMAND":
            return self._pay(ast)
        return "No operation."

    def _register(self, ast):
        identifier = ast["identifier"]
        id_type = ast["id_type"]
        if id_type == TOKEN_GUARDIAN_ID:
            Guardian.objects.create(guardian_id=identifier, name=f"Guardian {identifier}", phone="01000000000")
            return f"Guardian {identifier} registered."
        if id_type == TOKEN_CHILD_ID:
            guardian = Guardian.objects.order_by("created_at").first()
            Child.objects.create(
                child_id=identifier,
                name=f"Child {identifier}",
                age=6,
                guardian=guardian,
            )
            return f"Child {identifier} registered."
        if id_type == TOKEN_VEHICLE_ID:
            child = Child.objects.filter(pk=ast.get("child_id")).first()
            if child is None:
                child = Child.objects.order_by("-created_at").first()
            prefix = "".join(ch for ch in identifier if ch.isalpha())
            vehicle_type = prefix if prefix in dict(Vehicle.VehicleType.choices) else Vehicle.VehicleType.CAR
            Vehicle.objects.create(vehicle_id=identifier, vehicle_type=vehicle_type, child=child)
            return f"Vehicle {identifier} registered for child {child.child_id}."
        if id_type == TOKEN_SLOT_ID:
            ParkingSlot.objects.create(slot_id=identifier, status=ParkingSlot.Status.AVAILABLE)
            return f"Parking slot {identifier} registered."
        return f"Registered {identifier}."

    def _park(self, ast):
        vehicle = Vehicle.objects.get(pk=ast["vehicle_id"])
        slot = ParkingSlot.objects.get(pk=ast["slot_id"])
        park_vehicle(vehicle, slot)
        return f"Vehicle {vehicle.vehicle_id} assigned to {slot.slot_id}."

    def _entry(self, ast):
        vehicle = Vehicle.objects.get(pk=ast["vehicle_id"])
        record = process_entry(vehicle)
        return f"Vehicle {vehicle.vehicle_id} entered at slot {record.slot.slot_id}."

    def _exit(self, ast):
        vehicle = Vehicle.objects.get(pk=ast["vehicle_id"])
        record = process_exit(vehicle)
        return (
            f"Vehicle {vehicle.vehicle_id} exited from {record.slot.slot_id}. "
            f"Duration {record.duration_minutes} min. Fee {record.fee} BDT."
        )

    def _pay(self, ast):
        vehicle = Vehicle.objects.get(pk=ast["vehicle_id"])
        payment = collect_payment(vehicle)
        return (
            f"Payment completed for {vehicle.vehicle_id}. "
            f"Amount {payment.amount} BDT (PAY{payment.payment_id})."
        )
