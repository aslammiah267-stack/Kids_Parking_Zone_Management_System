from django.test import TestCase

from apps.compiler.errors import LexicalError
from apps.compiler.lexer import tokenize
from apps.compiler.tokens import TOKEN_KEYWORD, TOKEN_SLOT_ID, TOKEN_VEHICLE_ID


class LexerTests(TestCase):
    def test_valid_park_command(self):
        tokens = tokenize("PARK CAR101 SLOT05")
        self.assertEqual([t.token_type for t in tokens], [TOKEN_KEYWORD, TOKEN_VEHICLE_ID, TOKEN_SLOT_ID])
        self.assertEqual([t.lexeme for t in tokens], ["PARK", "CAR101", "SLOT05"])

    def test_invalid_character(self):
        with self.assertRaises(LexicalError) as ctx:
            tokenize("P@RK CAR101 SLOT05")
        self.assertIn("@", ctx.exception.message)

    def test_unknown_keyword(self):
        with self.assertRaises(LexicalError) as ctx:
            tokenize("HELLO CAR101")
        self.assertIn("Unknown keyword", ctx.exception.message)

    def test_invalid_id(self):
        with self.assertRaises(LexicalError) as ctx:
            tokenize("PARK CARX SLOT05")
        self.assertIn("Invalid ID", ctx.exception.message)
