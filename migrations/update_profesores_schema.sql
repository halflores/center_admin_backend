-- Migration to refactor Professors schema
-- 1. Create niveles_formacion table
CREATE TABLE IF NOT EXISTS niveles_formacion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

-- 2. Insert default values
INSERT INTO niveles_formacion (nombre) VALUES 
('Estudiante'),
('Bachiller'),
('Licenciatura'),
('PostGrado'),
('Doctorado')
ON CONFLICT (nombre) DO NOTHING;

-- 3. Alter profesores table
-- Drop old columns
ALTER TABLE profesores DROP COLUMN IF EXISTS titulo_academico;
ALTER TABLE profesores DROP COLUMN IF EXISTS especialidad;
ALTER TABLE profesores DROP COLUMN IF EXISTS nivel_formacion;

-- Add new column and foreign key
ALTER TABLE profesores ADD COLUMN IF NOT EXISTS nivel_formacion_id INTEGER REFERENCES niveles_formacion(id);

-- 4. Grant permissions for new table (if role 6 exists)
-- Ensure 'niveles_formacion' function exists
INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'niveles_formacion', 'Gestión de Niveles de Formación', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'niveles_formacion');

-- Ensure permissions exist
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre = 'niveles_formacion'
AND a.nombre IN ('create', 'read', 'update', 'delete')
AND NOT EXISTS (
    SELECT 1 FROM permisos p
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
);

-- Grant permissions to role 6
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id
FROM permisos p
JOIN funciones f ON p.funcion_id = f.id
WHERE f.nombre = 'niveles_formacion'
AND NOT EXISTS (
    SELECT 1 FROM rol_permisos rp
    WHERE rp.rol_id = 6 AND rp.permiso_id = p.id
);
