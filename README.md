# Kids Parking Zone Management System

University **Compiler Design** project that combines a real parking-zone operations system with a custom command language:

**KPCL — Kids Parking Command Language**

## 1. Project overview

The application manages a children's recreational parking zone (toy cars, electric cars, bikes). Staff can register guardians, children and vehicles, assign slots, process entry/exit, calculate fees and collect payments.

The distinctive academic component is the KPCL compiler. Commands typed in the Compiler Console pass through lexical analysis, token generation, syntax analysis, semantic analysis, intermediate code generation, and execution against the database.

## 2. Technology stack

- Frontend: React 18 + Vite + Recharts
- Backend: Django 5 + Django REST Framework + SimpleJWT
- Database: SQLite
- Compiler module: Python (independent package under `backend/apps/compiler/`)

## 3. Architecture

```
React Frontend
      | REST / JWT
Django REST Framework
      |
      ├── Authentication (Admin / Staff)
      ├── Guardians / Children / Vehicles
      ├── Parking slots & records
      ├── Payments & reports
      └── KPCL Compiler
            ├── Lexer
            ├── Parser
            ├── Semantic analyzer
            ├── Intermediate code generator
            └── Executor → SQLite
```

See `docs/architecture.md` for a fuller diagram.

## 4. Installation

Requires **Python 3.11+** and **Node.js 18+**.

## 5. Backend setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

API: http://127.0.0.1:8000/api/

## 6. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173/

Vite proxies `/api` to Django.

## 7. Database setup

SQLite file: `backend/db.sqlite3` (created by `migrate`).  
Fee rules live in `ParkingSettings` (first 30 minutes = 20 BDT, each extra 30 minutes = 10 BDT) and can be changed from **Settings**.

## 8. How to run the project

1. Start backend (`python manage.py runserver`)
2. Start frontend (`npm run dev`)
3. Open the React app and sign in
4. Open **KPCL Compiler** for the viva demonstration

## 9. KPCL language specification

See `docs/kpcl-language.md`.

Supported commands:

```
REGISTER CHILD101
REGISTER CAR101
PARK CAR101 SLOT05
ENTRY CAR101
EXIT CAR101
PAY CAR101
```

## 10. Compiler architecture

See `docs/compiler-design.md`.

Pipeline:

Input → Lexical Analysis → Tokens → Syntax Analysis → Semantic Analysis → Intermediate Code → Execution → Output

## 11. API documentation

See `docs/api.md`.

## 12. Demo commands

Successful flow (use after `seed_demo`; `CHILD101` / `CAR101` are not in the seed set, `SLOT05` is free):

```
REGISTER CHILD101
REGISTER CAR101
PARK CAR101 SLOT05
ENTRY CAR101
EXIT CAR101
PAY CAR101
```

Error demonstrations:

```
PARK CAR999 SLOT05          # SEMANTIC_ERROR — unregistered vehicle
PARK SLOT05                 # SYNTAX_ERROR — missing VEHICLE_ID
P@RK CAR101 SLOT05          # LEXICAL_ERROR — invalid character '@'
```

## 13. Testing

```bash
cd backend
python manage.py test
```

```bash
cd frontend
npm test
```

## 14. Future enhancements

- PostgreSQL and multi-branch sites
- Printed tickets / QR codes
- Guardian mobile check-in
- Richer KPCL (IF, loops, batch files)
- Audit log of every compiler execution

## Demo login credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Parking staff | `staff` | `staff123` |
