-- Migration: Add descuento column to detalle_venta table
-- Date: 2025-11-29
-- Description: Adds a descuento (discount) column to store discount amounts for each sale detail

-- Add descuento column to detalle_venta table
ALTER TABLE detalle_venta 
ADD COLUMN descuento NUMERIC(10, 2) DEFAULT 0.00 NOT NULL;

-- Add comment to the column
COMMENT ON COLUMN detalle_venta.descuento IS 'Discount amount applied to this sale detail item';

-- Update existing records to have 0.00 discount (already done by DEFAULT, but explicit for clarity)
UPDATE detalle_venta SET descuento = 0.00 WHERE descuento IS NULL;
