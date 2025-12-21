-- Migration: Add payment tracking fields to caja_movimientos
-- Date: 2025-12-19
-- Description: Add metodo_pago and numero_voucher columns to track payment information

ALTER TABLE caja_movimientos 
ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(50),
ADD COLUMN IF NOT EXISTS numero_voucher VARCHAR(100);

-- Add comments for documentation
COMMENT ON COLUMN caja_movimientos.metodo_pago IS 'Payment method: EFECTIVO, TARJETA, TRANSFERENCIA, QR';
COMMENT ON COLUMN caja_movimientos.numero_voucher IS 'Voucher or reference number for the transaction';
