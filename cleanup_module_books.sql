-- Script de Limpieza: Resetear Disponibilidad de Libros y Limpiar Préstamos de Prueba
-- =====================================================================================

-- OPCIÓN 1: Solo resetear disponibilidad de libros (mantener préstamos)
-- -----------------------------------------------------------------------
UPDATE libros 
SET cantidad_disponible = cantidad_total
WHERE id IN (1, 2, 3);  -- IDs de los libros del módulo

-- Verificar resultado
SELECT id, titulo, cantidad_total, cantidad_disponible 
FROM libros 
WHERE id IN (1, 2, 3);


-- OPCIÓN 2: Eliminar préstamos de prueba Y resetear disponibilidad
-- -----------------------------------------------------------------
-- ADVERTENCIA: Esto eliminará TODOS los préstamos del módulo 1

-- Paso 1: Eliminar multas asociadas a préstamos del módulo
DELETE FROM multas_prestamo 
WHERE prestamo_id IN (
    SELECT id FROM prestamos WHERE modulo_id = 1
);

-- Paso 2: Eliminar préstamos del módulo
DELETE FROM prestamos 
WHERE modulo_id = 1;

-- Paso 3: Resetear disponibilidad de libros
UPDATE libros 
SET cantidad_disponible = cantidad_total
WHERE id IN (
    SELECT libro_id FROM modulo_libros WHERE modulo_id = 1
);

-- Verificar resultado
SELECT 
    l.id, 
    l.titulo, 
    l.cantidad_total, 
    l.cantidad_disponible,
    COUNT(p.id) as prestamos_activos
FROM libros l
LEFT JOIN prestamos p ON l.id = p.libro_id AND p.estado = 'ACTIVO'
WHERE l.id IN (SELECT libro_id FROM modulo_libros WHERE modulo_id = 1)
GROUP BY l.id, l.titulo, l.cantidad_total, l.cantidad_disponible;


-- OPCIÓN 3: Eliminar SOLO préstamos de prueba de hoy
-- ----------------------------------------------------
-- Más seguro: solo elimina préstamos creados hoy

DELETE FROM multas_prestamo 
WHERE prestamo_id IN (
    SELECT id FROM prestamos 
    WHERE modulo_id = 1 
    AND DATE(created_at) = CURRENT_DATE
);

DELETE FROM prestamos 
WHERE modulo_id = 1 
AND DATE(created_at) = CURRENT_DATE;

UPDATE libros 
SET cantidad_disponible = cantidad_total
WHERE id IN (SELECT libro_id FROM modulo_libros WHERE modulo_id = 1);


-- VERIFICACIÓN FINAL
-- ------------------
SELECT 
    'Libros' as tabla,
    COUNT(*) as total,
    SUM(cantidad_disponible) as disponibles,
    SUM(cantidad_total) as total_copias
FROM libros
WHERE id IN (SELECT libro_id FROM modulo_libros WHERE modulo_id = 1)

UNION ALL

SELECT 
    'Préstamos Activos' as tabla,
    COUNT(*) as total,
    NULL as disponibles,
    NULL as total_copias
FROM prestamos
WHERE modulo_id = 1 AND estado = 'ACTIVO';
