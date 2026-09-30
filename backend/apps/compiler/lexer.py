"""KPCL Lexical Analyzer.

Lexical analysis is the first compiler phase. It reads the raw command string
character by character, groups characters into lexemes, and classifies each
lexeme as a token (KEYWORD, CHILD_ID, VEHICLE_ID, SLOT_ID, NUMBER, INVALID).
"""

import re

from .errors import LexicalError
from .tokens import (
    KEYWORDS,
    TOKEN_CHILD_ID,
    TOKEN_GUARDIAN_ID,
    TOKEN_INVALID,
    TOKEN_KEYWORD,
    TOKEN_NUMBER,
    TOKEN_SLOT_ID,
    TOKEN_VEHICLE_ID,
    Token,
)

CHILD_RE = re.compile(r"^CHILD\d+$", re.IGNORECASE)
VEHICLE_RE = re.compile(r"^(CAR|BIKE|TOY|VEH|BUS)\d+$", re.IGNORECASE)
SLOT_RE = re.compile(r"^SLOT\d+$", re.IGNORECASE)
GUARDIAN_RE = re.compile(r"^(GUARD|GUA)\d+$", re.IGNORECASE)
NUMBER_RE = re.compile(r"^\d+$")
IDENT_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*")


class Lexer:
    def __init__(self, source: str):
        self.source = source or ""
        self.length = len(self.source)
        self.index = 0

    def tokenize(self):
        for i, ch in enumerate(self.source):
            if ch.isspace() or ch.isalnum():
                continue
            raise LexicalError(
                f"Invalid character '{ch}'",
                extra={"character": ch, "position": i + 1},
            )
        tokens = []
        while self.index < self.length:
            ch = self.source[self.index]
            if ch.isspace():
                self.index += 1
                continue
            tokens.append(self._read_word())
        return tokens

    def _read_word(self):
        start = self.index
        while self.index < self.length and self.source[self.index].isalnum():
            self.index += 1
        lexeme = self.source[start:self.index]
        position = start + 1
        upper = lexeme.upper()
        token_type = self._classify(lexeme)
        if token_type == TOKEN_INVALID:
            prefixes = ("CHILD", "CAR", "BIKE", "TOY", "VEH", "BUS", "SLOT", "GUARD", "GUA")
            if any(upper.startswith(prefix) for prefix in prefixes):
                raise LexicalError(
                    f"Invalid ID '{lexeme}'",
                    extra={"lexeme": lexeme, "position": position},
                )
            if upper.isalpha() and upper not in KEYWORDS:
                raise LexicalError(
                    f"Unknown keyword '{lexeme}'",
                    extra={"lexeme": lexeme, "position": position},
                )
            raise LexicalError(
                f"Invalid ID '{lexeme}'",
                extra={"lexeme": lexeme, "position": position},
            )
        return Token(token_type=token_type, lexeme=lexeme.upper() if token_type == TOKEN_KEYWORD else lexeme.upper(), position=position)

    def _classify(self, lexeme: str) -> str:
        upper = lexeme.upper()
        if upper in KEYWORDS:
            return TOKEN_KEYWORD
        if CHILD_RE.match(upper):
            return TOKEN_CHILD_ID
        if VEHICLE_RE.match(upper):
            return TOKEN_VEHICLE_ID
        if SLOT_RE.match(upper):
            return TOKEN_SLOT_ID
        if GUARDIAN_RE.match(upper):
            return TOKEN_GUARDIAN_ID
        if NUMBER_RE.match(upper):
            return TOKEN_NUMBER
        return TOKEN_INVALID


def tokenize(source: str):
    """Convenience wrapper used by the compiler pipeline and tests."""
    return Lexer(source).tokenize()
