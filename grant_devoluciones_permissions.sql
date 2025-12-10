-- Script to grant 'devoluciones.create' and 'devoluciones.read' permissions to role_id = 6

-- 1. Ensure 'devoluciones' function exists
INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'devoluciones', 'Gestión de Devoluciones', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'devoluciones');

-- 2. Ensure 'create' and 'read' actions exist
INSERT INTO acciones (nombre, created_at)
SELECT 'create', NOW()
WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'create');

INSERT INTO acciones (nombre, created_at)
SELECT 'read', NOW()
WHERE NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'read');

-- 3. Ensure permissions exist
-- devoluciones.create
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f, acciones a
WHERE f.nombre = 'devoluciones' AND a.nombre = 'create'
AND NOT EXISTS (
    SELECT 1 FROM permisos p
    JOIN funciones f2 ON p.funcion_id = f2.id
    JOIN acciones a2 ON p.accion_id = a2.id
    WHERE f2.nombre = 'devoluciones' AND a2.nombre = 'create'
);

-- devoluciones.read
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f, acciones a
WHERE f.nombre = 'devoluciones' AND a.nombre = 'read'
AND NOT EXISTS (
    SELECT 1 FROM permisos p
    JOIN funciones f2 ON p.funcion_id = f2.id
    JOIN acciones a2 ON p.accion_id = a2.id
    WHERE f2.nombre = 'devoluciones' AND a2.nombre = 'read'
);

-- 4. Grant permissions to role_id = 6
-- Grant devoluciones.create
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id
FROM permisos p
JOIN funciones f ON p.funcion_id = f.id
JOIN acciones a ON p.accion_id = a.id
WHERE f.nombre = 'devoluciones' AND a.nombre = 'create'
AND NOT EXISTS (
    SELECT 1 FROM rol_permisos rp
    WHERE rp.rol_id = 6 AND rp.permiso_id = p.id
);

-- Grant devoluciones.read
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id
FROM permisos p
JOIN funciones f ON p.funcion_id = f.id
JOIN acciones a ON p.accion_id = a.id
WHERE f.nombre = 'devoluciones' AND a.nombre = 'read'
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
WHERE r.id = 6 AND f.nombre = 'devoluciones';
