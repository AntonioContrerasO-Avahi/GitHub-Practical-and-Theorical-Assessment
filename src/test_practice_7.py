"""
Test script for Practice 7 - OAuth2 + JWT Bearer Auth
------------------------------------------------------
Requires the server to be running:
    fastapi dev src/practice_7.py

Run this script with:
    python src/test_practice_7.py
"""

import requests

BASE_URL = "http://127.0.0.1:8000"

# ── helpers ──────────────────────────────────────────────────────────────────

def separator(title: str):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print('─' * 50)

def show(label: str, response: requests.Response):
    status = response.status_code
    icon = "✅" if status < 400 else "❌"
    print(f"{icon}  [{status}] {label}")
    print(f"     {response.json()}")


# ── test cases ────────────────────────────────────────────────────────────────

def test_public_healthcheck():
    separator("Public endpoint — no auth required")
    r = requests.get(f"{BASE_URL}/healthcheck")
    show("GET /healthcheck", r)
    assert r.status_code == 200


def test_register_user():
    separator("Register a new user")

    # Valid registration
    r = requests.post(f"{BASE_URL}/users/register", json={
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpass123",
        "confirm_password": "testpass123",
    })
    show("POST /users/register (valid)", r)
    assert r.status_code in (201, 409)  # 409 if already exists from a prior run

    # Duplicate username
    r = requests.post(f"{BASE_URL}/users/register", json={
        "username": "testuser",
        "full_name": "Another User",
        "password": "testpass123",
        "confirm_password": "testpass123",
    })
    show("POST /users/register (duplicate username)", r)
    assert r.status_code == 409

    # Mismatched passwords
    r = requests.post(f"{BASE_URL}/users/register", json={
        "username": "anotheruser",
        "full_name": "Another User",
        "password": "abc123",
        "confirm_password": "xyz999",
    })
    show("POST /users/register (mismatched passwords)", r)
    assert r.status_code == 422


def test_login():
    separator("Login — POST /token")

    # Valid credentials
    r = requests.post(f"{BASE_URL}/token", data={
        "username": "testuser",
        "password": "testpass123",
    })
    show("POST /token (valid credentials)", r)
    assert r.status_code == 200
    assert "access_token" in r.json()
    token = r.json()["access_token"]

    # Wrong password
    r = requests.post(f"{BASE_URL}/token", data={
        "username": "testuser",
        "password": "wrongpassword",
    })
    show("POST /token (wrong password)", r)
    assert r.status_code == 401

    # Non-existent user
    r = requests.post(f"{BASE_URL}/token", data={
        "username": "ghost",
        "password": "irrelevant",
    })
    show("POST /token (non-existent user)", r)
    assert r.status_code == 401

    return token


def test_protected_endpoints(token: str):
    separator("Protected endpoints — Bearer token")
    headers = {"Authorization": f"Bearer {token}"}

    # GET /user/me with valid token
    r = requests.get(f"{BASE_URL}/user/me", headers=headers)
    show("GET /user/me (valid token)", r)
    assert r.status_code == 200

    # GET /secret with valid token
    r = requests.get(f"{BASE_URL}/secret", headers=headers)
    show("GET /secret (valid token)", r)
    assert r.status_code == 200

    # GET /user/me with no token
    r = requests.get(f"{BASE_URL}/user/me")
    show("GET /user/me (no token)", r)
    assert r.status_code == 401

    # GET /secret with invalid token
    r = requests.get(f"{BASE_URL}/secret", headers={"Authorization": "Bearer invalid.token.here"})
    show("GET /secret (invalid token)", r)
    assert r.status_code == 401


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🚀 Practice 7 — OAuth2 + JWT Test Suite")
    print("   Make sure the server is running: fastapi dev src/practice_7.py\n")

    try:
        test_public_healthcheck()
        test_register_user()
        token = test_login()
        test_protected_endpoints(token)

        print(f"\n{'═' * 50}")
        print("  ✅  All tests passed!")
        print('═' * 50)

    except AssertionError as e:
        print(f"\n{'═' * 50}")
        print(f"  ❌  Test failed: {e}")
        print('═' * 50)
    except requests.exceptions.ConnectionError:
        print("\n❌  Could not connect to the server.")
        print("   Start it first with: fastapi dev src/practice_7.py")
