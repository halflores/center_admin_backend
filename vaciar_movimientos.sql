-- Script para vaciar movimientos de ventas, ingresos, devoluciones y productos
-- PRECAUCIÓN: Este script eliminará datos permanentemente.

BEGIN;

-- 1. Vaciar Tablas de Detalle y Movimientos (Hojas del árbol de dependencias)
DELETE FROM movimientos_inventario;
DELETE FROM detalle_venta;
DELETE FROM detalle_ingreso;
DELETE FROM detalle_devolucion;
DELETE FROM carrito_compras;
DELETE FROM precios_producto;
DELETE FROM descuentos_estudiante;
DELETE FROM paquete_productos;

-- 2. Desvincular Ventas de Inscripciones (Para no borrar las inscripciones)
-- Si desea borrar inscripciones también, agregue: DELETE FROM inscripcion_paquete;
UPDATE inscripcion_paquete SET venta_id = NULL;

-- 3. Vaciar Tablas Principales de Movimientos
DELETE FROM devoluciones;
DELETE FROM ventas;
DELETE FROM ingresos;

-- 4. Vaciar Catálogo de Productos
DELETE FROM productos;

-- Opcional: Reiniciar contadores de ID (si usa PostgreSQL)
-- ALTER SEQUENCE movimientos_inventario_id_seq RESTART WITH 1;
-- ALTER SEQUENCE ventas_id_seq RESTART WITH 1;
-- ...etc...

COMMIT;
