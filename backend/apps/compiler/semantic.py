"""KPCL Semantic Analyzer.

Semantic analysis checks meaning after the program is syntactically valid.
It consults the parking database so invalid operations never reach execution.
"""

from apps.children.models import Child
from apps.guardians.models import Guardian
from apps.parking.models import ParkingRecord, ParkingSlot
from apps.payments.models import Payment
from apps.vehicles.models import Vehicle

from .errors import SemanticError
from .tokens import TOKEN_CHILD_ID, TOKEN_GUARDIAN_ID, TOKEN_SLOT_ID, TOKEN_VEHICLE_ID


class SemanticAnalyzer:
    def analyze(self, ast):
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
        raise SemanticError(f"Unknown command type '{command_type}'.")

    def _register(self, ast):
        identifier = ast["identifier"]
        id_type = ast["id_type"]
        if id_type == TOKEN_CHILD_ID:
            if Child.objects.filter(pk=identifier).exists():
                raise SemanticError(f"Child {identifier} is already registered.")
            if not Guardian.objects.exists():
                raise SemanticError("No guardian exists. Register a guardian first or seed demo data.")
        elif id_type == TOKEN_VEHICLE_ID:
            if Vehicle.objects.filter(pk=identifier).exists():
                raise SemanticError(f"Vehicle {identifier} is already registered.")
            child = self._resolve_child_for_vehicle(identifier)
            if child is None:
                raise SemanticError(
                    f"Cannot register {identifier}: no child is available. Register a child first."
                )
            ast = {**ast, "child_id": child.child_id}
        elif id_type == TOKEN_SLOT_ID:
            if ParkingSlot.objects.filter(pk=identifier).exists():
                raise SemanticError(f"Slot {identifier} is already registered.")
        elif id_type == TOKEN_GUARDIAN_ID:
            if Guardian.objects.filter(pk=identifier).exists():
                raise SemanticError(f"Guardian {identifier} is already registered.")
        else:
            raise SemanticError(f"Cannot register identifier type {id_type}.")
        return ast

    def _resolve_child_for_vehicle(self, vehicle_id):
        digits = "".join(ch for ch in vehicle_id if ch.isdigit())
        if digits:
            child = Child.objects.filter(pk=f"CHILD{digits}").first()
            if child:
                return child
        return Child.objects.order_by("-created_at").first()

    def _require_vehicle(self, vehicle_id):
        vehicle = (
            Vehicle.objects.select_related("child", "child__guardian")
            .filter(pk=vehicle_id)
            .first()
        )
        if not vehicle:
            raise SemanticError(f"Vehicle {vehicle_id} is not registered.")
        return vehicle

    def _park(self, ast):
        vehicle = self._require_vehicle(ast["vehicle_id"])
        slot = ParkingSlot.objects.filter(pk=ast["slot_id"]).first()
        if not slot:
            raise SemanticError(f"Parking slot {ast['slot_id']} does not exist.")
        if slot.status == ParkingSlot.Status.OCCUPIED:
            raise SemanticError(f"{slot.slot_id} is already occupied.")
        active = ParkingRecord.objects.filter(
            vehicle=vehicle, status__in=[ParkingRecord.Status.RESERVED, ParkingRecord.Status.ACTIVE]
        ).exists()
        if active:
            raise SemanticError(f"Vehicle {vehicle.vehicle_id} is already parked.")
        return {**ast, "child_id": vehicle.child.child_id, "guardian_id": vehicle.child.guardian.guardian_id}

    def _entry(self, ast):
        vehicle = self._require_vehicle(ast["vehicle_id"])
        record = ParkingRecord.objects.filter(
            vehicle=vehicle, status__in=[ParkingRecord.Status.RESERVED, ParkingRecord.Status.ACTIVE]
        ).first()
        if record is None:
            raise SemanticError(
                f"Vehicle {vehicle.vehicle_id} is not assigned to a slot. Use PARK before ENTRY."
            )
        if record.status == ParkingRecord.Status.ACTIVE:
            raise SemanticError(f"Vehicle {vehicle.vehicle_id} has already entered the zone.")
        return ast

    def _exit(self, ast):
        vehicle = self._require_vehicle(ast["vehicle_id"])
        record = ParkingRecord.objects.filter(vehicle=vehicle, status=ParkingRecord.Status.ACTIVE).first()
        if record is None:
            reserved = ParkingRecord.objects.filter(
                vehicle=vehicle, status=ParkingRecord.Status.RESERVED
            ).exists()
            if reserved:
                raise SemanticError(
                    f"Vehicle {vehicle.vehicle_id} is reserved but has not entered. Complete ENTRY first."
                )
            raise SemanticError(f"Vehicle {vehicle.vehicle_id} is not currently parked.")
        return ast

    def _pay(self, ast):
        vehicle = self._require_vehicle(ast["vehicle_id"])
        record = (
            ParkingRecord.objects.filter(vehicle=vehicle, status=ParkingRecord.Status.EXITED)
            .order_by("-exit_time")
            .first()
        )
        if record is None:
            paid = ParkingRecord.objects.filter(
                vehicle=vehicle, status=ParkingRecord.Status.PAID
            ).exists()
            if paid and not ParkingRecord.objects.filter(
                vehicle=vehicle, status=ParkingRecord.Status.EXITED
            ).exists():
                raise SemanticError(f"No unpaid parking record for {vehicle.vehicle_id}.")
            raise SemanticError(
                f"Payment can only happen when there is a valid exited parking record for {vehicle.vehicle_id}."
            )
        if record.payments.filter(payment_status=Payment.Status.COMPLETED).exists():
            raise SemanticError(f"Parking record for {vehicle.vehicle_id} is already paid.")
        return {**ast, "record_id": record.record_id}


def analyze(ast):
    return SemanticAnalyzer().analyze(ast)
