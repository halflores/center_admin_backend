-- Script to grant ALL permissions to role_id = 6
-- Also ensures that permissions for the new academic structure modules exist.

-- 1. Ensure new functions exist
INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'programas', 'Gestión de Programas Académicos', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'programas');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'niveles', 'Gestión de Niveles Académicos', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'niveles');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'modulos', 'Gestión de Módulos', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'modulos');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'profesores', 'Gestión de Profesores', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'profesores');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'cursos', 'Gestión de Cursos', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'cursos');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'horarios', 'Gestión de Horarios', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'horarios');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'inscripciones', 'Gestión de Inscripciones', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'inscripciones');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'pagos_profesores', 'Gestión de Pagos a Profesores', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'pagos_profesores');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'niveles_formacion', 'Gestión de Niveles de Formación', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'niveles_formacion');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'aulas', 'Gestión de Aulas', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'aulas');

-- 2. Ensure actions exist (standard CRUD)
INSERT INTO acciones (nombre, created_at)
SELECT 'create', NOW()
WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'create');

INSERT INTO acciones (nombre, created_at)
SELECT 'read', NOW()
WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'read');

INSERT INTO acciones (nombre, created_at)
SELECT 'update', NOW()
WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'update');

INSERT INTO acciones (nombre, created_at)
SELECT 'delete', NOW()
WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'delete');

-- 3. Ensure permissions exist for all new functions and actions
-- We use a cross join to generate all combinations for the new functions
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre IN ('programas', 'niveles', 'modulos', 'profesores', 'cursos', 'horarios', 'inscripciones', 'pagos_profesores', 'niveles_formacion', 'aulas')
AND a.nombre IN ('create', 'read', 'update', 'delete')
AND NOT EXISTS (
    SELECT 1 FROM permisos p
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
);

-- 4. Grant ALL permissions to role_id = 6
-- This grants every permission currently in the 'permisos' table to role 6
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id
FROM permisos p
WHERE NOT EXISTS (
    SELECT 1 FROM rol_permisos rp
    WHERE rp.rol_id = 6 AND rp.permiso_id = p.id
);

-- Verification
SELECT COUNT(*) as total_permissions_granted
FROM rol_permisos
WHERE rol_id = 6;
