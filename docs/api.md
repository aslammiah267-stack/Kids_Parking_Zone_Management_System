# REST API

Base URL: `http://127.0.0.1:8000/api/`

All endpoints except login/refresh require header:

`Authorization: Bearer <access_token>`

## Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login/` | `{ username, password }` → `{ access, refresh, user }` |
| POST | `/auth/refresh/` | Refresh JWT |
| GET | `/auth/me/` | Current user |

## Resources (ViewSets)

| Method | Path |
|--------|------|
| CRUD | `/guardians/` |
| CRUD | `/children/` |
| CRUD | `/vehicles/` |
| GET `/vehicles/{id}/history/` | Vehicle parking history |
| CRUD | `/parking-slots/` |
| GET | `/parking-records/` |
| POST | `/parking-records/park/` `{ vehicle_id, slot_id }` |
| POST | `/parking-records/entry/` `{ vehicle_id, slot_id? }` |
| POST | `/parking-records/exit/` `{ vehicle_id }` |
| GET | `/parking-records/preview/?vehicle_id=` |
| GET/POST | `/payments/` |
| GET | `/reports/dashboard/` |
| GET | `/reports/summary/` |
| GET/PUT | `/settings/parking/` |

Query params on parking records: `vehicle`, `slot`, `status`, `from`, `to`, `search`, `page`, `page_size`.

## Compiler

`POST /compiler/execute/`

Request:

```json
{ "command": "PARK CAR101 SLOT05" }
```

Success:

```json
{
  "success": true,
  "command": "PARK CAR101 SLOT05",
  "tokens": [
    { "token_type": "KEYWORD", "lexeme": "PARK", "position": 1 },
    { "token_type": "VEHICLE_ID", "lexeme": "CAR101", "position": 6 },
    { "token_type": "SLOT_ID", "lexeme": "SLOT05", "position": 13 }
  ],
  "syntax_valid": true,
  "semantic_valid": true,
  "intermediate_code": [
    { "instruction": "LOAD", "operand": "CAR101" },
    { "instruction": "CHECK", "operand": "SLOT05" }
  ],
  "result": "Vehicle CAR101 assigned to SLOT05."
}
```

Error:

```json
{
  "success": false,
  "error_type": "SEMANTIC_ERROR",
  "message": "Vehicle CAR999 is not registered.",
  "tokens": [],
  "syntax_valid": true,
  "semantic_valid": false
}
```

Multiple newline-separated commands are executed sequentially; processing stops at the first error.
