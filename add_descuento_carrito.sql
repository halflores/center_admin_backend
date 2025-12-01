-- Add descuento column to carrito_compras table
ALTER TABLE carrito_compras 
ADD COLUMN IF NOT EXISTS descuento NUMERIC(10, 2) DEFAULT 0.0;

-- Update existing records to have 0.0 as default
UPDATE carrito_compras 
SET descuento = 0.0 
WHERE descuento IS NULL;
