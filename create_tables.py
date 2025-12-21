import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from app.db.session import engine
from app.models.models import Base

def create_tables():
    print("Creating tables...")
    try:
        # Create all tables defined in Base.metadata
        # checkfirst=True is default, so it won't recreate existing tables
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
