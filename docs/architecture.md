# System architecture

## Layers

1. **Presentation** — React SPA (`frontend/`). Dashboard, CRUD screens, entry/exit, payments, reports, and the KPCL compiler console.
2. **API** — Django REST Framework (`backend/config/urls.py`). JWT authentication. Role-aware permissions (Admin vs Staff).
3. **Domain services** — Parking fee calculation (`apps/parking/fees.py`), entry/exit transactions (`apps/parking/services.py`), payments (`apps/payments/services.py`).
4. **Compiler** — Isolated package `apps/compiler/` so the viva can walk file-by-file without mixing UI code.
5. **Persistence** — SQLite with unique business IDs, foreign keys, and a partial unique constraint: one active/reserved parking record per vehicle.

## Request flow for a KPCL command

```
Compiler UI
   POST /api/compiler/execute/  { "command": "PARK CAR101 SLOT05" }
        │
        ▼
pipeline.compile_script()
        │
        ├── lexer.tokenize()
        ├── parser.parse()
        ├── semantic.analyze()     # reads Django models, no writes
        ├── intermediate_code.generate()
        └── executor.execute()     # only if previous phases succeeded
                └── parking.services.park_vehicle()  (atomic)
```

The executor never runs if the lexer, parser, or semantic analyzer failed.

## Apps

| App | Responsibility |
|-----|----------------|
| `users` | Custom `User` with `ADMIN` / `STAFF` roles, JWT login |
| `guardians` | Guardian CRUD |
| `children` | Children linked to one guardian |
| `vehicles` | Vehicles linked to one child |
| `parking` | Slots, records, fee settings, seed command |
| `payments` | Payment collection after exit |
| `compiler` | KPCL pipeline |
| `reports` | Dashboard and summary aggregates |
