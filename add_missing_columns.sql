ALTER TABLE pagos_nomina ADD COLUMN IF NOT EXISTS nro_transaccion VARCHAR(100);
-- Verify other columns just in case
ALTER TABLE pagos_nomina ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(50);
-- fecha_pago already existed as per models.py history
