-- Script to grant permissions for Cash Closure Report features to Role ID 6
-- Date: 2025-12-19
-- Description: Grants access to financial reports with payment tracking

-- 1. Ensure Funciones exist
INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'reportes_caja', 'Reportes de cierre de caja y flujo de efectivo', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'reportes_caja');

-- Note: If 'finanzas' or 'caja' functions don't exist, create them
INSERT INTO funciones (nombre, descripcion, created_at)
SELECT 'finanzas', 'Gestión financiera y flujo de caja', NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'finanzas');

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
-- Reportes de Caja
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f, acciones a
WHERE f.nombre = 'reportes_caja' AND a.nombre IN ('read', 'create')
AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
);

-- Finanzas (if needed for full access)
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f, acciones a
WHERE f.nombre = 'finanzas' AND a.nombre IN ('create', 'read', 'update', 'delete')
AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
);

-- 4. Assign Permisos to Role ID 6
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id
FROM permisos p
JOIN funciones f ON p.funcion_id = f.id
WHERE f.nombre IN ('reportes_caja', 'finanzas')
AND NOT EXISTS (
    SELECT 1 FROM rol_permisos rp 
    WHERE rp.rol_id = 6 AND rp.permiso_id = p.id
);

-- Verification Query (run this to check the permissions were granted)
SELECT r.nombre as rol, f.nombre as funcion, a.nombre as accion 
FROM rol_permisos rp
JOIN roles r ON rp.rol_id = r.id
JOIN permisos p ON rp.permiso_id = p.id
JOIN funciones f ON p.funcion_id = f.id
JOIN acciones a ON p.accion_id = a.id
WHERE r.id = 6 AND f.nombre IN ('reportes_caja', 'finanzas')
ORDER BY f.nombre, a.nombre;
