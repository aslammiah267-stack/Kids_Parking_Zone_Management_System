from dataclasses import asdict, dataclass


@dataclass
class Token:
    """Token produced by the KPCL lexical analyzer."""

    token_type: str
    lexeme: str
    position: int

    def to_dict(self):
        return asdict(self)


KEYWORDS = {
    "REGISTER": "KEYWORD",
    "PARK": "KEYWORD",
    "ENTRY": "KEYWORD",
    "EXIT": "KEYWORD",
    "PAY": "KEYWORD",
}

TOKEN_KEYWORD = "KEYWORD"
TOKEN_CHILD_ID = "CHILD_ID"
TOKEN_VEHICLE_ID = "VEHICLE_ID"
TOKEN_SLOT_ID = "SLOT_ID"
TOKEN_GUARDIAN_ID = "GUARDIAN_ID"
TOKEN_NUMBER = "NUMBER"
TOKEN_INVALID = "INVALID"
TOKEN_EOF = "EOF"
