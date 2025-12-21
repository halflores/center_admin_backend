"""
Migration: Add payment tracking fields to caja_movimientos
Date: 2025-12-19
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    engine = create_engine(settings.DATABASE_URL)
    
    migration_sql = """
    -- Add payment tracking fields to caja_movimientos
    ALTER TABLE caja_movimientos 
    ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(50),
    ADD COLUMN IF NOT EXISTS numero_voucher VARCHAR(100);
    
    -- Add comments for documentation
    COMMENT ON COLUMN caja_movimientos.metodo_pago IS 'Payment method: EFECTIVO, TARJETA, TRANSFERENCIA, QR';
    COMMENT ON COLUMN caja_movimientos.numero_voucher IS 'Voucher or reference number for the transaction';
    """
    
    with engine.connect() as conn:
        conn.execute(text(migration_sql))
        conn.commit()
        print("✓ Migration completed successfully!")
        print("  - Added metodo_pago column to caja_movimientos")
        print("  - Added numero_voucher column to caja_movimientos")

if __name__ == "__main__":
    run_migration()
