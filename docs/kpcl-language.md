# KPCL — Kids Parking Command Language

KPCL is a small **command language** (not a general-purpose programming language). Each line is one command.

## Tokens

| Token type | Example lexemes |
|------------|-----------------|
| `KEYWORD` | `REGISTER`, `PARK`, `ENTRY`, `EXIT`, `PAY` |
| `CHILD_ID` | `CHILD101` |
| `VEHICLE_ID` | `CAR101`, `BIKE003`, `TOY004`, `BUS009` |
| `SLOT_ID` | `SLOT05` |
| `GUARDIAN_ID` | `GUARD01` |
| `NUMBER` | `30` |
| `INVALID` | rejected by the lexer |

Identifiers are normalized to uppercase. Whitespace is ignored. Any non-alphanumeric character (for example `@`) is a **lexical error**.

## Context-free grammar

```
COMMAND            → REGISTER_COMMAND
                   | PARK_COMMAND
                   | ENTRY_COMMAND
                   | EXIT_COMMAND
                   | PAY_COMMAND

REGISTER_COMMAND   → REGISTER ID
PARK_COMMAND       → PARK VEHICLE_ID SLOT_ID
ENTRY_COMMAND      → ENTRY VEHICLE_ID
EXIT_COMMAND       → EXIT VEHICLE_ID
PAY_COMMAND        → PAY VEHICLE_ID
```

`ID` is `CHILD_ID | VEHICLE_ID | SLOT_ID | GUARDIAN_ID`.

## Operational meaning

| Command | Effect |
|---------|--------|
| `REGISTER CHILD101` | Creates a child (requires at least one guardian in the database) |
| `REGISTER CAR101` | Creates a vehicle, preferably linked to `CHILD101` |
| `PARK CAR101 SLOT05` | Reserves an available slot (occupies it) |
| `ENTRY CAR101` | Starts the parking timer on a reserved assignment |
| `EXIT CAR101` | Calculates duration and fee, frees the slot |
| `PAY CAR101` | Completes payment for the latest exited unpaid record |

## Error classes

- **LEXICAL_ERROR** — illegal character or unknown keyword / invalid ID
- **SYNTAX_ERROR** — tokens do not match the grammar (`PARK SLOT05`)
- **SEMANTIC_ERROR** — grammar OK but meaning is illegal (`PARK CAR999 SLOT05`)
- **VALIDATION_ERROR / DATABASE_ERROR** — REST/CRUD layer
- **AUTHENTICATION_ERROR** — missing or invalid JWT
