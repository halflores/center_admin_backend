-- Script to grant 'movimientos.create' permission to role_id = 6

-- 1. Ensure 'movimientos' function exists
INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'movimientos', 'Gestión de Movimientos de Inventario', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'movimientos');

-- 2. Ensure 'create' action exists
INSERT INTO acciones (nombre, created_at)
SELECT 'create', NOW()
WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'create');

-- 3. Ensure permission 'movimientos.create' exists
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f, acciones a
WHERE f.nombre = 'movimientos' AND a.nombre = 'create'
AND NOT EXISTS (
    SELECT 1 FROM permisos p
    JOIN funciones f2 ON p.funcion_id = f2.id
    JOIN acciones a2 ON p.accion_id = a2.id
    WHERE f2.nombre = 'movimientos' AND a2.nombre = 'create'
);

-- 4. Grant permission to role_id = 6
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id
FROM permisos p
JOIN funciones f ON p.funcion_id = f.id
JOIN acciones a ON p.accion_id = a.id
WHERE f.nombre = 'movimientos' AND a.nombre = 'create'
AND NOT EXISTS (
    SELECT 1 FROM rol_permisos rp
    WHERE rp.rol_id = 6 AND rp.permiso_id = p.id
);

-- Verification
SELECT r.nombre as rol, f.nombre as funcion, a.nombre as accion
FROM rol_permisos rp
JOIN roles r ON rp.rol_id = r.id
JOIN permisos p ON rp.permiso_id = p.id
JOIN funciones f ON p.funcion_id = f.id
JOIN acciones a ON p.accion_id = a.id
WHERE r.id = 6 AND f.nombre = 'movimientos';
