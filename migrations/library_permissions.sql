-- 1. Insert functions for Library Module
INSERT INTO funciones (nombre, descripcion, created_at) VALUES 
('generos', 'Gestión de Géneros Literarios', NOW()),
('editoriales', 'Gestión de Editoriales', NOW()),
('autores', 'Gestión de Autores', NOW()),
('libros', 'Gestión de Libros', NOW()),
('prestamos', 'Gestión de Préstamos', NOW()),
('reservas', 'Gestión de Reservas', NOW())
ON CONFLICT (nombre) DO NOTHING;

-- 2. Grant permissions to Administrator role (rol_id = 1)
-- We assume actions 'read', 'create', 'update', 'delete' already exist with ids 1, 2, 3, 4 respectively
-- If not sure, we can lookup, but standard approach is using subqueries

-- Function: generos
INSERT INTO permisos (funcion_id, accion_id) 
SELECT f.id, a.id FROM funciones f, acciones a 
WHERE f.nombre = 'generos' AND a.nombre IN ('read', 'create', 'update', 'delete')
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 1, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'generos'
ON CONFLICT DO NOTHING;

-- Function: editoriales
INSERT INTO permisos (funcion_id, accion_id) 
SELECT f.id, a.id FROM funciones f, acciones a 
WHERE f.nombre = 'editoriales' AND a.nombre IN ('read', 'create', 'update', 'delete')
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 1, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'editoriales'
ON CONFLICT DO NOTHING;

-- Function: autores
INSERT INTO permisos (funcion_id, accion_id) 
SELECT f.id, a.id FROM funciones f, acciones a 
WHERE f.nombre = 'autores' AND a.nombre IN ('read', 'create', 'update', 'delete')
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 1, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'autores'
ON CONFLICT DO NOTHING;

-- Function: libros
INSERT INTO permisos (funcion_id, accion_id) 
SELECT f.id, a.id FROM funciones f, acciones a 
WHERE f.nombre = 'libros' AND a.nombre IN ('read', 'create', 'update', 'delete')
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 1, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'libros'
ON CONFLICT DO NOTHING;

-- Function: prestamos
INSERT INTO permisos (funcion_id, accion_id) 
SELECT f.id, a.id FROM funciones f, acciones a 
WHERE f.nombre = 'prestamos' AND a.nombre IN ('read', 'create', 'update', 'delete')
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 1, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'prestamos'
ON CONFLICT DO NOTHING;

-- Function: reservas
INSERT INTO permisos (funcion_id, accion_id) 
SELECT f.id, a.id FROM funciones f, acciones a 
WHERE f.nombre = 'reservas' AND a.nombre IN ('read', 'create', 'update', 'delete')
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 1, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'reservas'
ON CONFLICT DO NOTHING;
