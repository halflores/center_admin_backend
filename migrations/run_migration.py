"""
Migration script to add proveedores table and update ingresos
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "institute_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "")
)

cursor = conn.cursor()

try:
    print("Creating proveedores table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            direccion VARCHAR(255),
            celular VARCHAR(20),
            nombre_responsable VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✓ Proveedores table created")
    
    print("Creating ingresos table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingresos (
            id SERIAL PRIMARY KEY,
            proveedor VARCHAR(150),
            proveedor_id INTEGER REFERENCES proveedores(id) ON DELETE SET NULL,
            nro_factura VARCHAR(50),
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER REFERENCES usuarios(id),
            total DECIMAL(10, 2) NOT NULL DEFAULT 0,
            estado VARCHAR(20) DEFAULT 'COMPLETADO',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✓ Ingresos table created")
    
    print("Creating detalle_ingreso table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ingreso (
            id SERIAL PRIMARY KEY,
            ingreso_id INTEGER NOT NULL REFERENCES ingresos(id) ON DELETE CASCADE,
            producto_id INTEGER NOT NULL REFERENCES productos(id),
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            costo_unitario DECIMAL(10, 2) NOT NULL,
            subtotal DECIMAL(10, 2) NOT NULL
        );
    """)
    print("✓ Detalle_ingreso table created")
    
    print("Creating indexes...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ingresos_proveedor_id ON ingresos(proveedor_id);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_detalle_ingreso_ingreso ON detalle_ingreso(ingreso_id);
    """)
    print("✓ Indexes created")
    
    conn.commit()
    print("\n✅ Migration completed successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Migration failed: {e}")
    raise
finally:
    cursor.close()
    conn.close()
