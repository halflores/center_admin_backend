-- Script SQL adaptado para agregar permisos de acceso al menú "Módulos y Libros"
-- Basado en el esquema real de la base de datos

-- ============================================================
-- 1. CREAR FUNCIÓN "modulo_libros"
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'modulo_libros') THEN
        INSERT INTO funciones (nombre, descripcion, created_at)
        VALUES (
            'modulo_libros',
            'Gestión de asociaciones entre módulos y libros',
            CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Función "modulo_libros" creada exitosamente';
    ELSE
        RAISE NOTICE 'La función "modulo_libros" ya existe';
    END IF;
END $$;

-- ============================================================
-- 2. CREAR ACCIONES (si no existen globalmente)
-- ============================================================

DO $$
BEGIN
    -- Crear acción READ
    IF NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'read') THEN
        INSERT INTO acciones (nombre, descripcion, created_at)
        VALUES ('read', 'Lectura/Consulta', CURRENT_TIMESTAMP);
        RAISE NOTICE 'Acción "read" creada';
    END IF;
    
    -- Crear acción CREATE
    IF NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'create') THEN
        INSERT INTO acciones (nombre, descripcion, created_at)
        VALUES ('create', 'Creación', CURRENT_TIMESTAMP);
        RAISE NOTICE 'Acción "create" creada';
    END IF;
    
    -- Crear acción UPDATE
    IF NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'update') THEN
        INSERT INTO acciones (nombre, descripcion, created_at)
        VALUES ('update', 'Actualización', CURRENT_TIMESTAMP);
        RAISE NOTICE 'Acción "update" creada';
    END IF;
    
    -- Crear acción DELETE
    IF NOT EXISTS (SELECT 1 FROM acciones WHERE nombre = 'delete') THEN
        INSERT INTO acciones (nombre, descripcion, created_at)
        VALUES ('delete', 'Eliminación', CURRENT_TIMESTAMP);
        RAISE NOTICE 'Acción "delete" creada';
    END IF;
END $$;

-- ============================================================
-- 3. CREAR PERMISOS (función + acción)
-- ============================================================

DO $$
DECLARE
    v_funcion_id INTEGER;
    v_accion_read_id INTEGER;
    v_accion_create_id INTEGER;
    v_accion_update_id INTEGER;
    v_accion_delete_id INTEGER;
BEGIN
    -- Obtener IDs
    SELECT id INTO v_funcion_id FROM funciones WHERE nombre = 'modulo_libros';
    SELECT id INTO v_accion_read_id FROM acciones WHERE nombre = 'read';
    SELECT id INTO v_accion_create_id FROM acciones WHERE nombre = 'create';
    SELECT id INTO v_accion_update_id FROM acciones WHERE nombre = 'update';
    SELECT id INTO v_accion_delete_id FROM acciones WHERE nombre = 'delete';
    
    -- Crear permiso READ
    IF NOT EXISTS (
        SELECT 1 FROM permisos 
        WHERE funcion_id = v_funcion_id AND accion_id = v_accion_read_id
    ) THEN
        INSERT INTO permisos (funcion_id, accion_id)
        VALUES (v_funcion_id, v_accion_read_id);
        RAISE NOTICE 'Permiso modulo_libros.read creado';
    END IF;
    
    -- Crear permiso CREATE
    IF NOT EXISTS (
        SELECT 1 FROM permisos 
        WHERE funcion_id = v_funcion_id AND accion_id = v_accion_create_id
    ) THEN
        INSERT INTO permisos (funcion_id, accion_id)
        VALUES (v_funcion_id, v_accion_create_id);
        RAISE NOTICE 'Permiso modulo_libros.create creado';
    END IF;
    
    -- Crear permiso UPDATE
    IF NOT EXISTS (
        SELECT 1 FROM permisos 
        WHERE funcion_id = v_funcion_id AND accion_id = v_accion_update_id
    ) THEN
        INSERT INTO permisos (funcion_id, accion_id)
        VALUES (v_funcion_id, v_accion_update_id);
        RAISE NOTICE 'Permiso modulo_libros.update creado';
    END IF;
    
    -- Crear permiso DELETE
    IF NOT EXISTS (
        SELECT 1 FROM permisos 
        WHERE funcion_id = v_funcion_id AND accion_id = v_accion_delete_id
    ) THEN
        INSERT INTO permisos (funcion_id, accion_id)
        VALUES (v_funcion_id, v_accion_delete_id);
        RAISE NOTICE 'Permiso modulo_libros.delete creado';
    END IF;
END $$;

-- ============================================================
-- 4. ASIGNAR PERMISOS AL ROL ADMINISTRADOR (ID 1)
-- ============================================================

DO $$
DECLARE
    v_permiso_read_id INTEGER;
    v_permiso_create_id INTEGER;
    v_permiso_update_id INTEGER;
    v_permiso_delete_id INTEGER;
    v_rol_admin_id INTEGER := 1;
    v_funcion_id INTEGER;
    v_accion_read_id INTEGER;
    v_accion_create_id INTEGER;
    v_accion_update_id INTEGER;
    v_accion_delete_id INTEGER;
BEGIN
    -- Obtener IDs
    SELECT id INTO v_funcion_id FROM funciones WHERE nombre = 'modulo_libros';
    SELECT id INTO v_accion_read_id FROM acciones WHERE nombre = 'read';
    SELECT id INTO v_accion_create_id FROM acciones WHERE nombre = 'create';
    SELECT id INTO v_accion_update_id FROM acciones WHERE nombre = 'update';
    SELECT id INTO v_accion_delete_id FROM acciones WHERE nombre = 'delete';
    
    SELECT id INTO v_permiso_read_id FROM permisos 
    WHERE funcion_id = v_funcion_id AND accion_id = v_accion_read_id;
    
    SELECT id INTO v_permiso_create_id FROM permisos 
    WHERE funcion_id = v_funcion_id AND accion_id = v_accion_create_id;
    
    SELECT id INTO v_permiso_update_id FROM permisos 
    WHERE funcion_id = v_funcion_id AND accion_id = v_accion_update_id;
    
    SELECT id INTO v_permiso_delete_id FROM permisos 
    WHERE funcion_id = v_funcion_id AND accion_id = v_accion_delete_id;
    
    -- Asignar permiso READ
    IF NOT EXISTS (
        SELECT 1 FROM rol_permisos 
        WHERE rol_id = v_rol_admin_id AND permiso_id = v_permiso_read_id
    ) THEN
        INSERT INTO rol_permisos (rol_id, permiso_id, created_at)
        VALUES (v_rol_admin_id, v_permiso_read_id, CURRENT_TIMESTAMP);
        RAISE NOTICE 'Permiso READ asignado al rol administrador';
    END IF;
    
    -- Asignar permiso CREATE
    IF NOT EXISTS (
        SELECT 1 FROM rol_permisos 
        WHERE rol_id = v_rol_admin_id AND permiso_id = v_permiso_create_id
    ) THEN
        INSERT INTO rol_permisos (rol_id, permiso_id, created_at)
        VALUES (v_rol_admin_id, v_permiso_create_id, CURRENT_TIMESTAMP);
        RAISE NOTICE 'Permiso CREATE asignado al rol administrador';
    END IF;
    
    -- Asignar permiso UPDATE
    IF NOT EXISTS (
        SELECT 1 FROM rol_permisos 
        WHERE rol_id = v_rol_admin_id AND permiso_id = v_permiso_update_id
    ) THEN
        INSERT INTO rol_permisos (rol_id, permiso_id, created_at)
        VALUES (v_rol_admin_id, v_permiso_update_id, CURRENT_TIMESTAMP);
        RAISE NOTICE 'Permiso UPDATE asignado al rol administrador';
    END IF;
    
    -- Asignar permiso DELETE
    IF NOT EXISTS (
        SELECT 1 FROM rol_permisos 
        WHERE rol_id = v_rol_admin_id AND permiso_id = v_permiso_delete_id
    ) THEN
        INSERT INTO rol_permisos (rol_id, permiso_id, created_at)
        VALUES (v_rol_admin_id, v_permiso_delete_id, CURRENT_TIMESTAMP);
        RAISE NOTICE 'Permiso DELETE asignado al rol administrador';
    END IF;
END $$;

-- ============================================================
-- 5. VERIFICACIÓN FINAL
-- ============================================================

SELECT 
    f.nombre as funcion,
    a.nombre as accion,
    p.id as permiso_id,
    CASE WHEN rp.id IS NOT NULL THEN 'Asignado a Admin' ELSE 'No asignado' END as estado_admin
FROM funciones f
JOIN permisos p ON f.id = p.funcion_id
JOIN acciones a ON p.accion_id = a.id
LEFT JOIN rol_permisos rp ON p.id = rp.permiso_id AND rp.rol_id = 1
WHERE f.nombre = 'modulo_libros'
ORDER BY a.nombre;

-- ============================================================
-- SCRIPT COMPLETADO
-- ============================================================
