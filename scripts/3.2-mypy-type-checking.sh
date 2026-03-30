#!/usr/bin/env bash
# 3.2 Type Checking with mypy (~25 min)
set -euo pipefail

TMPDIR_BASE="$(pwd)/mypy-workspace"
rm -rf "$TMPDIR_BASE"
mkdir -p "$TMPDIR_BASE"
cd "$TMPDIR_BASE"

pip install --quiet mypy

# Create user_service.py with type hints
cat > user_service.py << 'EOF'
from typing import Union, Literal, TypedDict

def get_user_name(user_id: int) -> str:
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id, "Unknown")

def calculate_discount(price: float, discount_pct: float) -> float:
    return price * (1 - discount_pct / 100)

def format_id(id_value: Union[int, str]) -> str:
    return str(id_value)

def set_status(status: Literal["active", "inactive"]) -> None:
    print(f"Status: {status}")

class UserDict(TypedDict):
    id: int
    name: str

# Correct usage
user_name = get_user_name(1)
discount = calculate_discount(100.0, 10)

# Intentional type errors (comment in to test mypy):
# user_name_bad = get_user_name("alice")   # str, expects int
# discount_bad = calculate_discount("100", 10)  # str, expects float
EOF

echo "=== Running mypy on user_service.py ==="
mypy user_service.py

echo ""
echo "=== Now introducing intentional type errors ==="
cat > user_service_errors.py << 'EOF'
def get_user_name(user_id: int) -> str:
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id, "Unknown")

# Type error: passing str instead of int
result = get_user_name("alice")
EOF

mypy user_service_errors.py || echo "mypy caught the type error!"

# Cleanup
rm -rf "$TMPDIR_BASE"
