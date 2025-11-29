-- Migration: Add Proveedores table and update Ingresos
-- Created: 2025-11-28
-- Description: Creates proveedores table and adds proveedor_id foreign key to ingresos table

-- Step 1: Create proveedores table
CREATE TABLE IF NOT EXISTS proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    direccion VARCHAR(255),
    celular VARCHAR(20),
    nombre_responsable VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Add proveedor_id column to ingresos table
ALTER TABLE ingresos 
ADD COLUMN IF NOT EXISTS proveedor_id INTEGER REFERENCES proveedores(id) ON DELETE SET NULL;

-- Step 3: Create index on proveedor_id for better query performance
CREATE INDEX IF NOT EXISTS idx_ingresos_proveedor_id ON ingresos(proveedor_id);

-- Note: The old 'proveedor' text column is kept for backward compatibility
-- You can optionally migrate existing data or drop it later if needed

-- Optional: Migrate existing proveedor text data to new proveedores table
-- Uncomment the following if you want to migrate existing data:
/*
INSERT INTO proveedores (nombre)
SELECT DISTINCT proveedor 
FROM ingresos 
WHERE proveedor IS NOT NULL AND proveedor != ''
ON CONFLICT DO NOTHING;

UPDATE ingresos i
SET proveedor_id = p.id
FROM proveedores p
WHERE i.proveedor = p.nombre AND i.proveedor IS NOT NULL;
*/
