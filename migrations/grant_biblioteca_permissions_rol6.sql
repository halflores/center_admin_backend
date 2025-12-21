-- Script para otorgar permisos de biblioteca al Rol ID 6
-- Descripción: Crea funciones si no existen y otorga permisos completos

-- ==================== CREAR FUNCIONES SI NO EXISTEN ====================

INSERT INTO funciones (nombre, descripcion)
VALUES ('biblioteca', 'Gestión general de biblioteca')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO funciones (nombre, descripcion)
VALUES ('libros', 'Gestión de libros')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO funciones (nombre, descripcion)
VALUES ('prestamos', 'Gestión de préstamos')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO funciones (nombre, descripcion)
VALUES ('multas', 'Gestión de multas')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO funciones (nombre, descripcion)
VALUES ('reservas', 'Gestión de reservas')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO funciones (nombre, descripcion)
VALUES ('generos_literarios', 'Gestión de géneros literarios')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO funciones (nombre, descripcion)
VALUES ('editoriales', 'Gestión de editoriales')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO funciones (nombre, descripcion)
VALUES ('autores', 'Gestión de autores')
ON CONFLICT (nombre) DO NOTHING;


-- ==================== CREAR PERMISOS Y ASIGNAR AL ROL 6 ====================

-- Para cada función, crear permisos y asignarlos al rol 6
DO $$
DECLARE
    func_record RECORD;
    accion_record RECORD;
    permiso_id_var INTEGER;
BEGIN
    -- Iterar sobre cada función de biblioteca
    FOR func_record IN 
        SELECT id, nombre FROM funciones 
        WHERE nombre IN ('biblioteca', 'libros', 'prestamos', 'multas', 'reservas', 
                        'generos_literarios', 'editoriales', 'autores')
    LOOP
        -- Para cada acción (read, create, update, delete)
        FOR accion_record IN 
            SELECT id FROM acciones WHERE nombre IN ('read', 'create', 'update', 'delete')
        LOOP
            -- Crear permiso si no existe
            INSERT INTO permisos (funcion_id, accion_id)
            VALUES (func_record.id, accion_record.id)
            ON CONFLICT DO NOTHING
            RETURNING id INTO permiso_id_var;
            
            -- Si el permiso ya existía, obtener su ID
            IF permiso_id_var IS NULL THEN
                SELECT id INTO permiso_id_var 
                FROM permisos 
                WHERE funcion_id = func_record.id AND accion_id = accion_record.id;
            END IF;
            
            -- Asignar permiso al rol 6
            INSERT INTO rol_permisos (rol_id, permiso_id)
            VALUES (6, permiso_id_var)
            ON CONFLICT DO NOTHING;
        END LOOP;
    END LOOP;
    
    RAISE NOTICE 'Permisos otorgados exitosamente al Rol ID 6';
END $$;


-- ==================== VERIFICACIÓN ====================

-- Mostrar permisos otorgados al Rol 6 para biblioteca
SELECT 
    r.nombre as rol,
    f.nombre as funcion,
    a.nombre as accion
FROM rol_permisos rp
JOIN roles r ON r.id = rp.rol_id
JOIN permisos p ON p.id = rp.permiso_id
JOIN funciones f ON f.id = p.funcion_id
JOIN acciones a ON a.id = p.accion_id
WHERE r.id = 6
AND f.nombre IN ('biblioteca', 'libros', 'prestamos', 'multas', 'reservas', 
                 'generos_literarios', 'editoriales', 'autores')
ORDER BY f.nombre, a.nombre;

-- Contar permisos otorgados
SELECT 
    f.nombre as funcion,
    COUNT(*) as total_permisos
FROM rol_permisos rp
JOIN permisos p ON p.id = rp.permiso_id
JOIN funciones f ON f.id = p.funcion_id
WHERE rp.rol_id = 6
AND f.nombre IN ('biblioteca', 'libros', 'prestamos', 'multas', 'reservas', 
                 'generos_literarios', 'editoriales', 'autores')
GROUP BY f.nombre
ORDER BY f.nombre;
