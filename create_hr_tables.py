from sqlalchemy import create_engine
from app.core.config import settings
from app.models.models import Base, Cargo, Empleado, Usuario

def create_hr_tables():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    print("Creating tables for HR module (Cargo, Empleado)...")
    # This will only create tables that don't exist
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_hr_tables()
