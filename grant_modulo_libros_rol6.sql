-- Script SQL para asignar permisos de módulo-libros al Rol ID 6
-- Este script asigna todos los permisos CRUD de modulo_libros al rol especificado

DO $$
DECLARE
    v_permiso_read_id INTEGER;
    v_permiso_create_id INTEGER;
    v_permiso_update_id INTEGER;
    v_permiso_delete_id INTEGER;
    v_rol_id INTEGER := 6;  -- Rol ID 6
    v_funcion_id INTEGER;
    v_accion_read_id INTEGER;
    v_accion_create_id INTEGER;
    v_accion_update_id INTEGER;
    v_accion_delete_id INTEGER;
BEGIN
    -- Obtener IDs de función y acciones
    SELECT id INTO v_funcion_id FROM funciones WHERE nombre = 'modulo_libros';
    SELECT id INTO v_accion_read_id FROM acciones WHERE nombre = 'read';
    SELECT id INTO v_accion_create_id FROM acciones WHERE nombre = 'create';
    SELECT id INTO v_accion_update_id FROM acciones WHERE nombre = 'update';
    SELECT id INTO v_accion_delete_id FROM acciones WHERE nombre = 'delete';
    
    -- Obtener IDs de permisos
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
        WHERE rol_id = v_rol_id AND permiso_id = v_permiso_read_id
    ) THEN
        INSERT INTO rol_permisos (rol_id, permiso_id)
        VALUES (v_rol_id, v_permiso_read_id);
        RAISE NOTICE 'Permiso READ asignado al rol %', v_rol_id;
    ELSE
        RAISE NOTICE 'Permiso READ ya estaba asignado al rol %', v_rol_id;
    END IF;
    
    -- Asignar permiso CREATE
    IF NOT EXISTS (
        SELECT 1 FROM rol_permisos 
        WHERE rol_id = v_rol_id AND permiso_id = v_permiso_create_id
    ) THEN
        INSERT INTO rol_permisos (rol_id, permiso_id)
        VALUES (v_rol_id, v_permiso_create_id);
        RAISE NOTICE 'Permiso CREATE asignado al rol %', v_rol_id;
    ELSE
        RAISE NOTICE 'Permiso CREATE ya estaba asignado al rol %', v_rol_id;
    END IF;
    
    -- Asignar permiso UPDATE
    IF NOT EXISTS (
        SELECT 1 FROM rol_permisos 
        WHERE rol_id = v_rol_id AND permiso_id = v_permiso_update_id
    ) THEN
        INSERT INTO rol_permisos (rol_id, permiso_id)
        VALUES (v_rol_id, v_permiso_update_id);
        RAISE NOTICE 'Permiso UPDATE asignado al rol %', v_rol_id;
    ELSE
        RAISE NOTICE 'Permiso UPDATE ya estaba asignado al rol %', v_rol_id;
    END IF;
    
    -- Asignar permiso DELETE
    IF NOT EXISTS (
        SELECT 1 FROM rol_permisos 
        WHERE rol_id = v_rol_id AND permiso_id = v_permiso_delete_id
    ) THEN
        INSERT INTO rol_permisos (rol_id, permiso_id)
        VALUES (v_rol_id, v_permiso_delete_id);
        RAISE NOTICE 'Permiso DELETE asignado al rol %', v_rol_id;
    ELSE
        RAISE NOTICE 'Permiso DELETE ya estaba asignado al rol %', v_rol_id;
    END IF;
END $$;

-- Verificación final
SELECT 
    r.nombre as rol,
    f.nombre as funcion,
    a.nombre as accion,
    'Asignado' as estado
FROM rol_permisos rp
JOIN permisos p ON rp.permiso_id = p.id
JOIN funciones f ON p.funcion_id = f.id
JOIN acciones a ON p.accion_id = a.id
JOIN roles r ON rp.rol_id = r.id
WHERE rp.rol_id = 6 AND f.nombre = 'modulo_libros'
ORDER BY a.nombre;

-- ============================================================
-- SCRIPT COMPLETADO
-- Para ejecutar: Get-Content grant_modulo_libros_rol6.sql | docker exec -i f0eab9c991af psql -U admin -d institute_db
-- ============================================================
