-- Grant permissions to Role ID 6 for Library Module
-- Functions: generos, editoriales, autores, libros, prestamos, reservas
-- Actions: read, create, update, delete

-- Function: generos
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'generos'
ON CONFLICT DO NOTHING;

-- Function: editoriales
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'editoriales'
ON CONFLICT DO NOTHING;

-- Function: autores
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'autores'
ON CONFLICT DO NOTHING;

-- Function: libros
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'libros'
ON CONFLICT DO NOTHING;

-- Function: prestamos
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'prestamos'
ON CONFLICT DO NOTHING;

-- Function: reservas
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 6, p.id FROM permisos p 
JOIN funciones f ON p.funcion_id = f.id 
WHERE f.nombre = 'reservas'
ON CONFLICT DO NOTHING;
