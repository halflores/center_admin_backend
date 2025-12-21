from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    print("Hashing '123456'...")
    h = pwd_context.hash("123456")
    print(f"Success: {h}")
    
    print("Hashing '5689421'...")
    h2 = pwd_context.hash("5689421")
    print(f"Success: {h2}")

    long_pass = "x" * 73
    print("Hashing 73 chars...")
    pwd_context.hash(long_pass)
except Exception as e:
    print(f"Error: {e}")
