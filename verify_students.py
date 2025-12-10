
import sys
import os

# Add the current directory to sys.path to allow imports
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import Estudiante
from app.schemas.estudiante import EstudianteResponse

def verify_students():
    db = SessionLocal()
    try:
        # Fetch all students like the endpoint does
        estudiantes = db.query(Estudiante).all()
        print(f"Found {len(estudiantes)} students in DB.")

        for i, est in enumerate(estudiantes):
            try:
                # Attempt to validate using Pydantic model
                EstudianteResponse.model_validate(est)
            except Exception as e:
                print(f"Validation failed for student ID {est.id}, Name: {est.nombres} {est.apellidos}")
                print(f"Error: {e}")
                # Print key attributes that might be causing issues
                print(f"  - campus_id: {est.campus_id}, campus: {est.campus}")
                print(f"  - responsables: {est.responsables}")
                print(f"  - fecha_nacimiento: {est.fecha_nacimiento} type: {type(est.fecha_nacimiento)}")
                print(f"  - created_at: {est.created_at} type: {type(est.created_at)}")
                
                # Check for nullable violations in basic fields
                if not est.nombres: print("  ! nombres is empty/None")
                if not est.apellidos: print("  ! apellidos is empty/None")
                
                return # Stop after first error for clarity

        print("All students validated successfully against EstudianteResponse.")

    except Exception as e:
        print(f"General error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_students()
