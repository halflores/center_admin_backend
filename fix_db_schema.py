import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import reflection

# Add current directory to path
sys.path.append(os.getcwd())
from app.db.session import SessionLocal

def fix_schema():
    db = SessionLocal()
    engine = db.get_bind()
    inspector = reflection.Inspector.from_engine(engine)
    
    columns = [c['name'] for c in inspector.get_columns('ventas')]
    print(f"Current columns in 'ventas': {columns}")
    
    with engine.connect() as conn:
        with conn.begin(): # Start transaction
            if 'tipo_transaccion_id' not in columns:
                print("Adding missing column: tipo_transaccion_id")
                # Using text() for raw SQL execution
                conn.execute(text("ALTER TABLE ventas ADD COLUMN tipo_transaccion_id INTEGER REFERENCES tipos_transaccion(id)"))
            else:
                print("Column 'tipo_transaccion_id' already exists.")
                
            if 'nro_voucher' not in columns:
                 print("Adding missing column: nro_voucher")
                 conn.execute(text("ALTER TABLE ventas ADD COLUMN nro_voucher VARCHAR(100)"))
            else:
                print("Column 'nro_voucher' already exists.")

    print("Schema update check complete.")

if __name__ == "__main__":
    try:
        fix_schema()
    except Exception as e:
        print(f"Error updating schema: {e}")
