-- Insert Permissions for Categoria Gasto
-- Function: finanzas, Resource: categorias, Actions: read, create, update, delete

DO $$
DECLARE
    v_funcion_id INTEGER;
    permiso_read_id INTEGER;
    rol_admin_id INTEGER;
BEGIN
    -- Ensure Function 'finanzas.categorias' exists
    INSERT INTO funciones (nombre, descripcion) VALUES ('finanzas.categorias', 'Gestión de Categorías de Gastos')
    ON CONFLICT (nombre) DO UPDATE SET descripcion = EXCLUDED.descripcion
    RETURNING id INTO v_funcion_id;

    -- Insert Permissions
    -- We assume actions 'read', 'create', 'update', 'delete' exist.
    -- We select their IDs and the funcion_id to insert into Permisos.
    
    INSERT INTO permisos (funcion_id, accion_id)
    SELECT v_funcion_id, id FROM acciones WHERE nombre IN ('read', 'create', 'update', 'delete')
    ON CONFLICT DO NOTHING;

    -- Assign to SuperAdmin (Rol ID 1 usually, or we search)
    SELECT id INTO rol_admin_id FROM roles WHERE nombre = 'SuperAdmin';
    
    IF rol_admin_id IS NOT NULL THEN
        INSERT INTO rol_permisos (rol_id, permiso_id)
        SELECT rol_admin_id, p.id
        FROM permisos p
        WHERE p.funcion_id = v_funcion_id
        ON CONFLICT DO NOTHING;
    END IF;

    -- Assign to Role ID 6 (User Request)
    INSERT INTO rol_permisos (rol_id, permiso_id)
    SELECT 6, p.id
    FROM permisos p
    WHERE p.funcion_id = v_funcion_id
    ON CONFLICT DO NOTHING;
    
END $$;
