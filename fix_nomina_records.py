import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to allow importing app modules
sys.path.append(os.getcwd())

from app.core.config import settings
from app.models.models import PagoNomina, CajaMovimiento
from app.schemas.financial import PagoNominaOut

def fix_nomina():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        pagos = db.query(PagoNomina).all()
        print(f"Checking {len(pagos)} records...")
        
        deleted_count = 0
        
        for pago in pagos:
            try:
                # Try to validate against schema
                # We need to manually construct the dict because fields might be missing in older records if they were not nullable? 
                # But here all new fields are nullable.
                
                # Check for critical missing data that might cause partial failures
                if not pago.usuario_empleado_id or not pago.monto:
                     print(f"Deleting invalid record ID {pago.id}: Missing critical fields")
                     delete_record(db, pago)
                     deleted_count += 1
                     continue

                # The schema validation might fail if we pass the ORM object directly and it's missing attributes expected by 'from_attributes'
                # But let's try to simulate the response model validation
                pago_out = PagoNominaOut.model_validate(pago)
                
            except Exception as e:
                print(f"Error validating record ID {pago.id}: {e}")
                print(f"Data: {pago.__dict__}")
                print(f"Deleting record ID {pago.id} due to validation error.")
                delete_record(db, pago)
                deleted_count += 1
        
        print(f"Finished. Deleted {deleted_count} problematic records.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

def delete_record(db, pago):
    # Also delete associated cash movement
    mov = db.query(CajaMovimiento).filter(
        CajaMovimiento.referencia_tabla == 'pagos_nomina',
        CajaMovimiento.referencia_id == pago.id
    ).first()
    
    if mov:
        db.delete(mov)
    
    db.delete(pago)
    db.commit()

if __name__ == "__main__":
    fix_nomina()
