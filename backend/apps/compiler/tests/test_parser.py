from django.test import TestCase

from apps.compiler.errors import KPCLSyntaxError
from apps.compiler.lexer import tokenize
from apps.compiler.parser import parse


class ParserTests(TestCase):
    def test_valid_park_command(self):
        ast = parse(tokenize("PARK CAR101 SLOT05"))
        self.assertEqual(ast["type"], "PARK_COMMAND")
        self.assertEqual(ast["vehicle_id"], "CAR101")
        self.assertEqual(ast["slot_id"], "SLOT05")

    def test_invalid_park_missing_vehicle(self):
        with self.assertRaises(KPCLSyntaxError) as ctx:
            parse(tokenize("PARK SLOT05"))
        self.assertIn("VEHICLE_ID", ctx.exception.message)

    def test_invalid_park_wrong_order(self):
        with self.assertRaises(KPCLSyntaxError):
            parse(tokenize("PARK SLOT05 CAR101"))

    def test_invalid_entry_command(self):
        with self.assertRaises(KPCLSyntaxError):
            parse(tokenize("ENTRY SLOT05"))

    def test_invalid_exit_command(self):
        with self.assertRaises(KPCLSyntaxError):
            parse(tokenize("EXIT"))
