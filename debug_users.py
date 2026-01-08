import sys
import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import Usuario

def debug_users():
    db = SessionLocal()
    try:
        users = db.query(Usuario).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Is Active: {user.is_active}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    debug_users()
