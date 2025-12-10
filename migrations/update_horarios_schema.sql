-- Create aulas table
CREATE TABLE IF NOT EXISTS aulas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    capacidad INTEGER,
    ubicacion VARCHAR(100)
);

-- Insert default aulas
INSERT INTO aulas (nombre, capacidad, ubicacion) VALUES 
('Rojo', 30, 'Piso 1'),
('Azul', 30, 'Piso 1'),
('Verde', 25, 'Piso 2'),
('Amarillo', 25, 'Piso 2'),
('Naranja', 20, 'Piso 3')
ON CONFLICT (nombre) DO NOTHING;

-- Alter horarios table
-- Note: This drops the existing 'aula' column and data!
ALTER TABLE horarios DROP COLUMN IF EXISTS aula;
ALTER TABLE horarios ADD COLUMN IF NOT EXISTS aula_id INTEGER REFERENCES aulas(id);

-- Grant permissions to role 6 (Admin)
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id
FROM permisos p
JOIN funciones f ON p.funcion_id = f.id
WHERE f.nombre = 'aulas'
AND NOT EXISTS (
    SELECT 1 FROM rol_permisos rp WHERE rp.rol_id = 6 AND rp.permiso_id = p.id
);

-- Ensure functions and actions exist (idempotent)
INSERT INTO funciones (nombre, descripcion) VALUES ('aulas', 'Gestión de Aulas') ON CONFLICT (nombre) DO NOTHING;

-- Insert permissions for aulas if they don't exist
DO $$
DECLARE
    func_id INTEGER;
    act_create INTEGER;
    act_read INTEGER;
    act_update INTEGER;
    act_delete INTEGER;
BEGIN
    SELECT id INTO func_id FROM funciones WHERE nombre = 'aulas';
    SELECT id INTO act_create FROM acciones WHERE nombre = 'create';
    SELECT id INTO act_read FROM acciones WHERE nombre = 'read';
    SELECT id INTO act_update FROM acciones WHERE nombre = 'update';
    SELECT id INTO act_delete FROM acciones WHERE nombre = 'delete';

    INSERT INTO permisos (funcion_id, accion_id) VALUES (func_id, act_create) ON CONFLICT DO NOTHING;
    INSERT INTO permisos (funcion_id, accion_id) VALUES (func_id, act_read) ON CONFLICT DO NOTHING;
    INSERT INTO permisos (funcion_id, accion_id) VALUES (func_id, act_update) ON CONFLICT DO NOTHING;
    INSERT INTO permisos (funcion_id, accion_id) VALUES (func_id, act_delete) ON CONFLICT DO NOTHING;
END $$;

-- Grant permissions again to be sure
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id
FROM permisos p
JOIN funciones f ON p.funcion_id = f.id
WHERE f.nombre = 'aulas'
AND NOT EXISTS (
    SELECT 1 FROM rol_permisos rp WHERE rp.rol_id = 6 AND rp.permiso_id = p.id
);
