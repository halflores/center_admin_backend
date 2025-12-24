
-- Corregir función del trigger que usa nombre de columna incorrecto
CREATE OR REPLACE FUNCTION actualizar_multa_on_devolucion()
RETURNS TRIGGER AS $$
BEGIN
    -- Corregido: usar fecha_devolucion_real en lugar de fecha_devolucion
    IF NEW.fecha_devolucion_real IS NOT NULL AND OLD.fecha_devolucion_real IS NULL THEN
        -- Si la fecha de devolución real es mayor a la esperada
        IF NEW.fecha_devolucion_real > NEW.fecha_devolucion_esperada THEN
            -- Calcular días de retraso
            NEW.dias_retraso = (NEW.fecha_devolucion_real - NEW.fecha_devolucion_esperada);
            -- Calcular multa (asumiendo 1.00 por día, ajustar según lógica de negocio si es necesario)
            NEW.monto_multa = NEW.dias_retraso * 1.00;
        ELSE
            NEW.dias_retraso = 0;
            NEW.monto_multa = 0;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
