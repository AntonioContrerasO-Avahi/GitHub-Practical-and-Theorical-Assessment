# Module 6: FastAPI Activities

A hands-on progressive series of 7 FastAPI practices covering REST APIs, authentication, password hashing, and JWT tokens.

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)

---

## Setup

```bash
# Install dependencies
uv sync
```

---

## Running a Practice

Use the launcher script to start any practice interactively:

```bash
./run.sh
```

You will see a menu:

```
=========================================
   FastAPI Module 6 - Practice Launcher
=========================================

  1)  Practice 1 - First REST API
  2)  Practice 2 - Defining Models
  3)  Practice 3 - Edit Objects
  4)  Practice 4 - Basic Auth
  5)  Practice 5 - User Registration
  6)  Practice 6 - Password Hashing
  7)  Practice 7 - OAuth2 + JWT

Select a practice (1-7):
```

Type a number and press Enter. The server starts at `http://127.0.0.1:8000`.

You can also run any practice directly:

```bash
fastapi dev src/practice_1.py   # or practice_2.py ... practice_7.py
```

Once running, open the Swagger docs at:

```
http://127.0.0.1:8000/docs
```

---

## Practice Overview

| # | Practice | Auth | Storage |
|---|----------|------|---------|
| 1 | First REST API | None | None |
| 2 | Defining Models | None | None |
| 3 | Edit Objects | None | In-memory dict |
| 4 | Basic Auth | HTTP Basic | In-memory dict |
| 5 | User Registration | HTTP Basic | In-memory dict |
| 6 | Password Hashing | HTTP Basic + bcrypt | In-memory dict |
| 7 | OAuth2 + JWT | Bearer token (JWT) | SQLite |

---

## Testing Practice 7

Practice 7 includes a dedicated test script that covers the full OAuth2 + JWT flow.

### 1. Start the server

```bash
fastapi dev src/practice_7.py
```

### 2. Run the tests (in a separate terminal)

```bash
python src/test_practice_7.py
```

### What the tests cover

| Test | Expected |
|------|----------|
| `GET /healthcheck` | `200` — public, no auth needed |
| `POST /users/register` (valid) | `201` — user created |
| `POST /users/register` (duplicate username) | `409` — conflict |
| `POST /users/register` (mismatched passwords) | `422` — validation error |
| `POST /token` (valid credentials) | `200` — returns JWT |
| `POST /token` (wrong password) | `401` — unauthorized |
| `POST /token` (non-existent user) | `401` — unauthorized |
| `GET /user/me` (valid token) | `200` — returns user info |
| `GET /secret` (valid token) | `200` — returns secret message |
| `GET /user/me` (no token) | `401` — unauthorized |
| `GET /secret` (invalid token) | `401` — unauthorized |

### Example output

```
🚀 Practice 7 — OAuth2 + JWT Test Suite
   Make sure the server is running: fastapi dev src/practice_7.py

──────────────────────────────────────────────────
  Public endpoint — no auth required
──────────────────────────────────────────────────
✅  [200] GET /healthcheck
     {'message': 'Hello There, this is public. No auth required'}

──────────────────────────────────────────────────
  Register a new user
──────────────────────────────────────────────────
✅  [201] POST /users/register (valid)
     {'message': 'User created', 'id': 1, 'username': 'testuser'}
❌  [409] POST /users/register (duplicate username)
     {'detail': "Username 'testuser' is already taken"}
❌  [422] POST /users/register (mismatched passwords)
     {'detail': [...]}

══════════════════════════════════════════════════
  ✅  All tests passed!
══════════════════════════════════════════════════
```

---

## Project Structure

```
.
├── run.sh                    # Interactive practice launcher
├── pyproject.toml
├── uv.lock
└── src/
    ├── practice_1.py         # Practice 1 - First REST API
    ├── practice_2.py         # Practice 2 - Defining Models
    ├── practice_3.py         # Practice 3 - Edit Objects
    ├── practice_4.py         # Practice 4 - Basic Auth
    ├── practice_5.py         # Practice 5 - User Registration
    ├── practice_6.py         # Practice 6 - Password Hashing
    ├── practice_7.py         # Practice 7 - OAuth2 + JWT
    ├── test_practice_7.py    # Test suite for Practice 7
    ├── main.py               # Full implementation (all practices)
    └── db/
        ├── schema.py         # SQLModel table + Pydantic models
        └── utils.py          # DB engine, session, JWT, bcrypt utils
```
