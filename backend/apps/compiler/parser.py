"""KPCL Syntax Analyzer (Parser).

The parser checks whether a token stream matches the KPCL context-free grammar:

    COMMAND           → REGISTER_COMMAND | PARK_COMMAND | ENTRY_COMMAND | EXIT_COMMAND | PAY_COMMAND
    REGISTER_COMMAND  → REGISTER ID
    PARK_COMMAND      → PARK VEHICLE_ID SLOT_ID
    ENTRY_COMMAND     → ENTRY VEHICLE_ID
    EXIT_COMMAND      → EXIT VEHICLE_ID
    PAY_COMMAND       → PAY VEHICLE_ID
"""

from .errors import KPCLSyntaxError
from .tokens import (
    TOKEN_CHILD_ID,
    TOKEN_GUARDIAN_ID,
    TOKEN_KEYWORD,
    TOKEN_SLOT_ID,
    TOKEN_VEHICLE_ID,
)


ID_TYPES = {TOKEN_CHILD_ID, TOKEN_VEHICLE_ID, TOKEN_GUARDIAN_ID, TOKEN_SLOT_ID}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def parse(self):
        if not self.tokens:
            raise KPCLSyntaxError("Empty command.")
        command = self._command()
        if self.index < len(self.tokens):
            extra = self.tokens[self.index]
            raise KPCLSyntaxError(
                f"Unexpected token '{extra.lexeme}' after a complete command."
            )
        return command

    def _current(self):
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def _accept_keyword(self, *names):
        token = self._current()
        if token and token.token_type == TOKEN_KEYWORD and token.lexeme in names:
            self.index += 1
            return token
        return None

    def _expect_type(self, expected_types, message):
        token = self._current()
        if token is None:
            raise KPCLSyntaxError(message)
        if token.token_type not in expected_types:
            raise KPCLSyntaxError(message)
        self.index += 1
        return token

    def _command(self):
        token = self._current()
        if not token or token.token_type != TOKEN_KEYWORD:
            raise KPCLSyntaxError("Command must start with a keyword: REGISTER, PARK, ENTRY, EXIT, or PAY.")
        keyword = token.lexeme
        if keyword == "REGISTER":
            return self._register()
        if keyword == "PARK":
            return self._park()
        if keyword == "ENTRY":
            return self._unary("ENTRY", "ENTRY_COMMAND")
        if keyword == "EXIT":
            return self._unary("EXIT", "EXIT_COMMAND")
        if keyword == "PAY":
            return self._unary("PAY", "PAY_COMMAND")
        raise KPCLSyntaxError(f"Unsupported command '{keyword}'.")

    def _register(self):
        self._accept_keyword("REGISTER")
        ident = self._current()
        if ident is None:
            raise KPCLSyntaxError("Expected ID after REGISTER.")
        if ident.token_type not in ID_TYPES:
            raise KPCLSyntaxError("Expected CHILD_ID, VEHICLE_ID, SLOT_ID, or GUARDIAN_ID after REGISTER.")
        self.index += 1
        return {
            "type": "REGISTER_COMMAND",
            "keyword": "REGISTER",
            "id_type": ident.token_type,
            "identifier": ident.lexeme,
        }

    def _park(self):
        self._accept_keyword("PARK")
        first = self._current()
        if first is None:
            raise KPCLSyntaxError("Expected VEHICLE_ID and SLOT_ID.")
        if first.token_type != TOKEN_VEHICLE_ID:
            raise KPCLSyntaxError("Expected VEHICLE_ID and SLOT_ID.")
        vehicle = self._expect_type({TOKEN_VEHICLE_ID}, "Expected VEHICLE_ID and SLOT_ID.")
        second = self._current()
        if second is None or second.token_type != TOKEN_SLOT_ID:
            raise KPCLSyntaxError("Expected VEHICLE_ID and SLOT_ID.")
        slot = self._expect_type({TOKEN_SLOT_ID}, "Expected VEHICLE_ID and SLOT_ID.")
        return {
            "type": "PARK_COMMAND",
            "keyword": "PARK",
            "vehicle_id": vehicle.lexeme,
            "slot_id": slot.lexeme,
        }

    def _unary(self, keyword, command_type):
        self._accept_keyword(keyword)
        vehicle = self._expect_type(
            {TOKEN_VEHICLE_ID},
            f"Expected VEHICLE_ID after {keyword}.",
        )
        return {
            "type": command_type,
            "keyword": keyword,
            "vehicle_id": vehicle.lexeme,
        }


def parse(tokens):
    return Parser(tokens).parse()
