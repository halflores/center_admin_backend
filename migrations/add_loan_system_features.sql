-- Migration: Add Loan System Features
-- Description: Adds support for loan types, late fees, module-book relationships, and fines

-- 1. Add new columns to prestamos table
ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS tipo_prestamo VARCHAR(20) DEFAULT 'PERSONAL';
-- Valores: 'PERSONAL', 'ACADEMICO'

ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS modulo_id INTEGER;
ALTER TABLE prestamos ADD CONSTRAINT fk_prestamos_modulo 
    FOREIGN KEY (modulo_id) REFERENCES modulos(id) ON DELETE SET NULL;

ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS dias_retraso INTEGER DEFAULT 0;
ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS monto_multa DECIMAL(10,2) DEFAULT 0.00;
ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS multa_pagada BOOLEAN DEFAULT FALSE;

-- 2. Create multas_prestamo table
CREATE TABLE IF NOT EXISTS multas_prestamo (
    id SERIAL PRIMARY KEY,
    prestamo_id INTEGER NOT NULL REFERENCES prestamos(id) ON DELETE CASCADE,
    dias_retraso INTEGER NOT NULL,
    monto_por_dia DECIMAL(10,2) DEFAULT 1.00,
    monto_total DECIMAL(10,2) NOT NULL,
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pagado BOOLEAN DEFAULT FALSE,
    fecha_pago TIMESTAMP,
    metodo_pago VARCHAR(50),
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create modulo_libros table (relationship between modules and books)
CREATE TABLE IF NOT EXISTS modulo_libros (
    id SERIAL PRIMARY KEY,
    modulo_id INTEGER NOT NULL REFERENCES modulos(id) ON DELETE CASCADE,
    libro_id INTEGER NOT NULL REFERENCES libros(id) ON DELETE CASCADE,
    orden INTEGER DEFAULT 1,
    obligatorio BOOLEAN DEFAULT TRUE,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(modulo_id, libro_id)
);

-- 4. Update reservas table if needed
ALTER TABLE reservas ADD COLUMN IF NOT EXISTS fecha_notificacion TIMESTAMP;
ALTER TABLE reservas ADD COLUMN IF NOT EXISTS fecha_expiracion TIMESTAMP;
ALTER TABLE reservas ADD COLUMN IF NOT EXISTS notificado BOOLEAN DEFAULT FALSE;

-- 5. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_prestamos_tipo ON prestamos(tipo_prestamo);
CREATE INDEX IF NOT EXISTS idx_prestamos_modulo ON prestamos(modulo_id);
CREATE INDEX IF NOT EXISTS idx_prestamos_estado ON prestamos(estado);
CREATE INDEX IF NOT EXISTS idx_prestamos_fecha_devolucion ON prestamos(fecha_devolucion_esperada);
CREATE INDEX IF NOT EXISTS idx_multas_prestamo ON multas_prestamo(prestamo_id);
CREATE INDEX IF NOT EXISTS idx_multas_pagado ON multas_prestamo(pagado);
CREATE INDEX IF NOT EXISTS idx_modulo_libros_modulo ON modulo_libros(modulo_id);
CREATE INDEX IF NOT EXISTS idx_modulo_libros_libro ON modulo_libros(libro_id);
CREATE INDEX IF NOT EXISTS idx_reservas_estado ON reservas(estado);
CREATE INDEX IF NOT EXISTS idx_reservas_notificado ON reservas(notificado);

-- 6. Add comments for documentation
COMMENT ON COLUMN prestamos.tipo_prestamo IS 'Tipo de préstamo: PERSONAL o ACADEMICO';
COMMENT ON COLUMN prestamos.modulo_id IS 'Módulo asociado si es préstamo académico';
COMMENT ON COLUMN prestamos.dias_retraso IS 'Días de retraso en la devolución';
COMMENT ON COLUMN prestamos.monto_multa IS 'Monto total de multa por retraso';
COMMENT ON COLUMN prestamos.multa_pagada IS 'Indica si la multa fue pagada';

COMMENT ON TABLE multas_prestamo IS 'Registro de multas por retraso en devolución de libros';
COMMENT ON TABLE modulo_libros IS 'Relación entre módulos académicos y libros asignados';

-- 7. Create function to calculate late fees
CREATE OR REPLACE FUNCTION calcular_multa_prestamo(p_prestamo_id INTEGER)
RETURNS TABLE(dias_retraso INTEGER, monto_multa DECIMAL) AS $$
DECLARE
    v_fecha_esperada DATE;
    v_fecha_devolucion DATE;
    v_dias INTEGER;
    v_monto DECIMAL;
BEGIN
    SELECT fecha_devolucion_esperada, fecha_devolucion
    INTO v_fecha_esperada, v_fecha_devolucion
    FROM prestamos
    WHERE id = p_prestamo_id;
    
    IF v_fecha_devolucion IS NULL THEN
        v_fecha_devolucion := CURRENT_DATE;
    END IF;
    
    IF v_fecha_devolucion > v_fecha_esperada THEN
        v_dias := v_fecha_devolucion - v_fecha_esperada;
        v_monto := v_dias * 1.00; -- 1 Bs por día
    ELSE
        v_dias := 0;
        v_monto := 0.00;
    END IF;
    
    RETURN QUERY SELECT v_dias, v_monto;
END;
$$ LANGUAGE plpgsql;

-- 8. Create trigger to update multa on return
CREATE OR REPLACE FUNCTION actualizar_multa_on_devolucion()
RETURNS TRIGGER AS $$
DECLARE
    v_multa RECORD;
BEGIN
    IF NEW.fecha_devolucion IS NOT NULL AND OLD.fecha_devolucion IS NULL THEN
        SELECT * INTO v_multa FROM calcular_multa_prestamo(NEW.id);
        
        NEW.dias_retraso := v_multa.dias_retraso;
        NEW.monto_multa := v_multa.monto_multa;
        
        IF v_multa.monto_multa > 0 THEN
            INSERT INTO multas_prestamo (
                prestamo_id, dias_retraso, monto_por_dia, monto_total
            ) VALUES (
                NEW.id, v_multa.dias_retraso, 1.00, v_multa.monto_multa
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_actualizar_multa ON prestamos;
CREATE TRIGGER trigger_actualizar_multa
    BEFORE UPDATE ON prestamos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_multa_on_devolucion();

-- 9. Insert sample data for testing (optional)
-- Uncomment to add sample module-book relationships
-- INSERT INTO modulo_libros (modulo_id, libro_id, orden, obligatorio, descripcion)
-- SELECT m.id, l.id, 1, true, 'Lectura obligatoria del módulo'
-- FROM modulos m
-- CROSS JOIN libros l
-- WHERE m.nombre LIKE '%Básico%' AND l.titulo LIKE '%Introducción%'
-- LIMIT 1;

COMMIT;
