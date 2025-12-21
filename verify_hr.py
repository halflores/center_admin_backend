from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import Cargo, Empleado, Usuario

def verify_hr():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create a test cargo
        print("Creating test cargo...")
        cargo_name = "Test Cargo - Verificacion"
        existing = db.query(Cargo).filter(Cargo.nombre == cargo_name).first()
        if existing:
            db.delete(existing)
            db.commit()
            
        new_cargo = Cargo(nombre=cargo_name, descripcion="Cargo de prueba")
        db.add(new_cargo)
        db.commit()
        db.refresh(new_cargo)
        print(f"Cargo created: ID={new_cargo.id}, Name={new_cargo.nombre}")
        
        # Clean up
        db.delete(new_cargo)
        db.commit()
        print("Verification successful: Cargo created and deleted.")
        
    except Exception as e:
        print(f"Verification Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_hr()
