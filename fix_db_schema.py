import os
import sys

# Ensure we can find the app modules
sys.path.append('/app')

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_schema():
    print(f"Connecting to DB: {settings.DATABASE_URL.replace(settings.DB_PASSWORD, '***')}")
    engine = create_engine(settings.DATABASE_URL)
    
    updates = [
        "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS usuario_id INTEGER REFERENCES usuarios(id);",
        "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS tipo_prestamo VARCHAR(50);",
        "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS modulo_id INTEGER REFERENCES modulos(id);",
        "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS dias_retraso INTEGER DEFAULT 0;",
        "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS monto_multa NUMERIC(10, 2) DEFAULT 0.00;",
        "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS multa_pagada BOOLEAN DEFAULT FALSE;"
    ]

    with engine.connect() as conn:
        for stmt in updates:
            try:
                conn.execute(text(stmt))
                print(f"SUCCESS: {stmt}")
            except Exception as e:
                print(f"WARNING: Could not execute '{stmt}'. Error: {e}")
        conn.commit()
    print("Schema update finished.")

if __name__ == "__main__":
    fix_schema()
