-- Script to setup permissions for HR Module and assign to Role ID 6

-- 1. Ensure Funciones exist
INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'cargos', 'Gestión de cargos y puestos de trabajo', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'cargos');

INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'empleados', 'Gestión de empleados y personal', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'empleados');

-- 2. Ensure Acciones exist (standard CRUD)
INSERT INTO acciones (nombre, created_at)
SELECT 'create', NOW() WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'create');
INSERT INTO acciones (nombre, created_at)
SELECT 'read', NOW() WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'read');
INSERT INTO acciones (nombre, created_at)
SELECT 'update', NOW() WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'update');
INSERT INTO acciones (nombre, created_at)
SELECT 'delete', NOW() WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'delete');

-- 3. Create Permisos (linking Funciones and Acciones)
-- Cargos
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f, acciones a
WHERE f.nombre = 'cargos' AND a.nombre IN ('create', 'read', 'update', 'delete')
AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
);

-- Empleados
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f, acciones a
WHERE f.nombre = 'empleados' AND a.nombre IN ('create', 'read', 'update', 'delete')
AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
);

-- 4. Assign Permisos to Role ID 6
-- We need to find the IDs of the permissions we just ensured exist
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id
FROM permisos p
JOIN funciones f ON p.funcion_id = f.id
WHERE f.nombre IN ('cargos', 'empleados')
AND NOT EXISTS (
    SELECT 1 FROM rol_permisos rp 
    WHERE rp.rol_id = 6 AND rp.permiso_id = p.id
);

-- Verification Query (Optional, for you to run to check)
-- SELECT r.nombre as rol, f.nombre as funcion, a.nombre as accion 
-- FROM rol_permisos rp
-- JOIN roles r ON rp.rol_id = r.id
-- JOIN permisos p ON rp.permiso_id = p.id
-- JOIN funciones f ON p.funcion_id = f.id
-- JOIN acciones a ON p.accion_id = a.id
-- WHERE r.id = 6 AND f.nombre IN ('cargos', 'empleados');
