-- Script to add 'anulado' column to 'movimientos_inventario' table

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'movimientos_inventario'
        AND column_name = 'anulado'
    ) THEN
        ALTER TABLE movimientos_inventario ADD COLUMN anulado BOOLEAN DEFAULT FALSE;
    END IF;
END $$;
