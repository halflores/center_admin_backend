from app.core.security import get_password_hash

try:
    pwd = "password123"
    print(f"Hashing password: {pwd}")
    hashed = get_password_hash(pwd)
    print(f"Hashed: {hashed}")
except Exception as e:
    print(f"Error: {e}")
