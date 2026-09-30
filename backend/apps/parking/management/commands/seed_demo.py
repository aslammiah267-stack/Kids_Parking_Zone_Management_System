from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.children.models import Child
from apps.guardians.models import Guardian
from apps.parking.fees import calculate_parking_fee
from apps.parking.models import ParkingRecord, ParkingSettings, ParkingSlot
from apps.payments.models import Payment
from apps.users.models import User
from apps.vehicles.models import Vehicle


class Command(BaseCommand):
    help = "Seed demo users, guardians, children, vehicles, slots, and parking records."

    def handle(self, *args, **options):
        ParkingSettings.get_solo()
        self._users()
        self._guardians_children_vehicles()
        self._slots_and_records()
        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
        self.stdout.write("Admin login: admin / admin123")
        self.stdout.write("Staff login: staff / staff123")

    def _users(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@kpzms.local",
                password="admin123",
                role=User.Role.ADMIN,
            )
        else:
            admin = User.objects.get(username="admin")
            admin.role = User.Role.ADMIN
            admin.set_password("admin123")
            admin.save()
        if not User.objects.filter(username="staff").exists():
            User.objects.create_user(
                username="staff",
                email="staff@kpzms.local",
                password="staff123",
                role=User.Role.STAFF,
                is_staff=True,
            )
        else:
            staff = User.objects.get(username="staff")
            staff.role = User.Role.STAFF
            staff.set_password("staff123")
            staff.save()

    def _guardians_children_vehicles(self):
        names = [
            ("Rahim Uddin", "01710000001"),
            ("Fatema Begum", "01710000002"),
            ("Karim Mia", "01710000003"),
            ("Nusrat Jahan", "01710000004"),
            ("Hasan Ali", "01710000005"),
            ("Sabrina Akter", "01710000006"),
            ("Jamal Hossain", "01710000007"),
            ("Tania Rahman", "01710000008"),
            ("Mahmudul Islam", "01710000009"),
            ("Ayesha Siddika", "01710000010"),
        ]
        guardians = []
        for i, (name, phone) in enumerate(names, start=1):
            gid = f"GUARD{i:02d}"
            guardian, _ = Guardian.objects.get_or_create(
                guardian_id=gid, defaults={"name": name, "phone": phone}
            )
            guardians.append(guardian)

        child_specs = [
            ("Ayaan", 5, 0),
            ("Mahi", 6, 0),
            ("Rayan", 7, 1),
            ("Inaya", 4, 1),
            ("Zayan", 8, 2),
            ("Hana", 5, 3),
            ("Ibrahim", 6, 3),
            ("Sara", 9, 4),
            ("Yusuf", 7, 5),
            ("Layla", 4, 5),
            ("Omar", 6, 6),
            ("Noor", 8, 7),
            ("Adam", 5, 8),
            ("Maryam", 7, 8),
            ("Idris", 6, 9),
        ]
        children = []
        for i, (name, age, gidx) in enumerate(child_specs, start=1):
            cid = f"CHILD{i:03d}"
            child, _ = Child.objects.get_or_create(
                child_id=cid,
                defaults={"name": name, "age": age, "guardian": guardians[gidx]},
            )
            children.append(child)

        types = [
            Vehicle.VehicleType.CAR,
            Vehicle.VehicleType.CAR,
            Vehicle.VehicleType.BIKE,
            Vehicle.VehicleType.TOY,
            Vehicle.VehicleType.CAR,
            Vehicle.VehicleType.BIKE,
            Vehicle.VehicleType.CAR,
            Vehicle.VehicleType.TOY,
            Vehicle.VehicleType.BUS,
            Vehicle.VehicleType.CAR,
            Vehicle.VehicleType.BIKE,
            Vehicle.VehicleType.CAR,
            Vehicle.VehicleType.TOY,
            Vehicle.VehicleType.CAR,
            Vehicle.VehicleType.BIKE,
        ]
        for i, vehicle_type in enumerate(types, start=1):
            prefix = {
                Vehicle.VehicleType.CAR: "CAR",
                Vehicle.VehicleType.BIKE: "BIKE",
                Vehicle.VehicleType.TOY: "TOY",
                Vehicle.VehicleType.BUS: "BUS",
            }[vehicle_type]
            vid = f"{prefix}{i:03d}"
            Vehicle.objects.get_or_create(
                vehicle_id=vid,
                defaults={"vehicle_type": vehicle_type, "child": children[i - 1]},
            )

    def _slots_and_records(self):
        for i in range(1, 21):
            ParkingSlot.objects.get_or_create(
                slot_id=f"SLOT{i:02d}",
                defaults={"status": ParkingSlot.Status.AVAILABLE},
            )

        now = timezone.now()
        occupied_pairs = [
            ("CAR001", "SLOT01", 25),
            ("CAR002", "SLOT02", 40),
            ("BIKE003", "SLOT03", 15),
            ("TOY004", "SLOT04", 70),
            ("CAR005", "SLOT06", 10),
            ("BIKE006", "SLOT08", 55),
        ]
        for vehicle_id, slot_id, minutes in occupied_pairs:
            slot = ParkingSlot.objects.get(pk=slot_id)
            vehicle = Vehicle.objects.get(pk=vehicle_id)
            if ParkingRecord.objects.filter(
                vehicle=vehicle, status__in=[ParkingRecord.Status.RESERVED, ParkingRecord.Status.ACTIVE]
            ).exists():
                continue
            slot.status = ParkingSlot.Status.OCCUPIED
            slot.save(update_fields=["status"])
            ParkingRecord.objects.create(
                vehicle=vehicle,
                slot=slot,
                status=ParkingRecord.Status.ACTIVE,
                entry_time=now - timedelta(minutes=minutes),
            )

        history = [
            ("CAR007", "SLOT10", 45, True),
            ("TOY008", "SLOT12", 90, True),
            ("BUS009", "SLOT15", 30, False),
        ]
        for vehicle_id, slot_id, minutes, paid in history:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
            slot = ParkingSlot.objects.get(pk=slot_id)
            if ParkingRecord.objects.filter(vehicle=vehicle, status__in=["EXITED", "PAID"]).exists():
                continue
            entry = now - timedelta(hours=3, minutes=minutes)
            exit_time = entry + timedelta(minutes=minutes)
            fee = calculate_parking_fee(minutes)
            record = ParkingRecord.objects.create(
                vehicle=vehicle,
                slot=slot,
                status=ParkingRecord.Status.PAID if paid else ParkingRecord.Status.EXITED,
                entry_time=entry,
                exit_time=exit_time,
                duration_minutes=minutes,
                fee=fee,
            )
            if paid:
                Payment.objects.create(
                    vehicle=vehicle,
                    parking_record=record,
                    amount=fee,
                    payment_status=Payment.Status.COMPLETED,
                )
