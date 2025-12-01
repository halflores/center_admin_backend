import sys
import os

# Add the current directory to sys.path to allow imports
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import Venta, Usuario

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Get the last created sale
    last_venta = db.query(Venta).order_by(Venta.id.desc()).first()

    if last_venta:
        print(f"Last Venta ID: {last_venta.id}")
        print(f"Usuario ID: {last_venta.usuario_id}")
        
        # Check if user exists with that ID
        if last_venta.usuario_id:
            user = db.query(Usuario).filter(Usuario.id == last_venta.usuario_id).first()
            if user:
                print(f"User found in DB: {user.nombre} {user.apellido}")
                print(f"User Rol ID: {user.rol_id}")
                print(f"User Email: {user.correo}")
            else:
                print("User ID not found in users table")
        
        # Check relationship
        if last_venta.usuario:
            print(f"Usuario Relationship Loaded: {last_venta.usuario.nombre} {last_venta.usuario.apellido}")
        else:
            print("Usuario relationship is None (Lazy loading might be inactive or failed)")

        # Test Pydantic Validation
        try:
            from app.schemas.venta import VentaResponse
            venta_response = VentaResponse.model_validate(last_venta)
            print("Pydantic Validation Successful")
            print(f"Response Usuario: {venta_response.usuario}")
            if venta_response.detalles:
                print(f"First Detail Product: {venta_response.detalles[0].producto}")
            else:
                print("No details in response")
            
            if venta_response.estudiante and venta_response.estudiante.campus:
                print(f"Campus: {venta_response.estudiante.campus.nombre}")
            else:
                print("Campus not found")

        except Exception as e:
            print(f"Pydantic Validation Failed: {e}")
            
    else:
        print("No ventas found")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
