from django.urls import reverse
from rest_framework.test import APITestCase

from apps.children.models import Child
from apps.compiler.pipeline import compile_command
from apps.guardians.models import Guardian
from apps.parking.models import ParkingSettings, ParkingSlot
from apps.users.models import User
from apps.vehicles.models import Vehicle


class ApiTests(APITestCase):
    def setUp(self):
        ParkingSettings.get_solo()
        self.admin = User.objects.create_user(username="admin", password="admin123", role=User.Role.ADMIN)
        self.guardian = Guardian.objects.create(guardian_id="GUARD01", name="G", phone="01700000000")
        self.child = Child.objects.create(child_id="CHILD101", name="Kid", age=6, guardian=self.guardian)
        ParkingSlot.objects.create(slot_id="SLOT05")
        self.client.force_authenticate(self.admin)

    def test_vehicle_api_create(self):
        response = self.client.post(
            "/api/vehicles/",
            {"vehicle_id": "CAR101", "vehicle_type": "CAR", "child": "CHILD101"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Vehicle.objects.filter(pk="CAR101").exists())

    def test_parking_api_entry_requires_park(self):
        Vehicle.objects.create(vehicle_id="CAR101", vehicle_type="CAR", child=self.child)
        response = self.client.post("/api/parking-records/entry/", {"vehicle_id": "CAR101"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_compiler_api_and_demo_flow(self):
        url = reverse("compiler-execute")
        register_child = self.client.post(url, {"command": "REGISTER CHILD102"}, format="json")
        self.assertTrue(register_child.data["success"])
        register_car = self.client.post(url, {"command": "REGISTER CAR102"}, format="json")
        self.assertTrue(register_car.data["success"])
        park = self.client.post(url, {"command": "PARK CAR102 SLOT05"}, format="json")
        self.assertTrue(park.data["success"])
        entry = self.client.post(url, {"command": "ENTRY CAR102"}, format="json")
        self.assertTrue(entry.data["success"])
        exit_res = self.client.post(url, {"command": "EXIT CAR102"}, format="json")
        self.assertTrue(exit_res.data["success"])
        pay = self.client.post(url, {"command": "PAY CAR102"}, format="json")
        self.assertTrue(pay.data["success"])

        semantic = compile_command("PARK CAR999 SLOT05")
        self.assertFalse(semantic["success"])
        self.assertEqual(semantic["error_type"], "SEMANTIC_ERROR")

        syntax = compile_command("PARK SLOT05")
        self.assertEqual(syntax["error_type"], "SYNTAX_ERROR")

        lexical = compile_command("P@RK CAR101 SLOT05")
        self.assertEqual(lexical["error_type"], "LEXICAL_ERROR")
