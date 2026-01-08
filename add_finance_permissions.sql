-- Script para agregar funciones y permisos del módulo de Finanzas
-- Basado en los endpoints existentes en financial.py

-- Primero, verificar si las funciones ya existen
-- Si no existen, insertarlas

-- Función: CAJA_SESIONES (para gestión de sesiones de caja)
INSERT INTO funciones (nombre, descripcion, activo, fecha_creacion)
SELECT 'CAJA_SESIONES', 'Gestión de sesiones de caja (abrir/cerrar)', TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'CAJA_SESIONES');

-- Función: GASTOS (para registro de gastos)
INSERT INTO funciones (nombre, descripcion, activo, fecha_creacion)
SELECT 'GASTOS', 'Registro y gestión de gastos', TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'GASTOS');

-- Función: CATEGORIAS_GASTO (para categorías de gastos)
INSERT INTO funciones (nombre, descripcion, activo, fecha_creacion)
SELECT 'CATEGORIAS_GASTO', 'Gestión de categorías de gastos', TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'CATEGORIAS_GASTO');

-- Función: INGRESOS_VARIOS (para ingresos varios)
INSERT INTO funciones (nombre, descripcion, activo, fecha_creacion)
SELECT 'INGRESOS_VARIOS', 'Registro de ingresos varios', TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'INGRESOS_VARIOS');

-- Función: CAJA_MOVIMIENTOS (para consulta de movimientos)
INSERT INTO funciones (nombre, descripcion, activo, fecha_creacion)
SELECT 'CAJA_MOVIMIENTOS', 'Consulta de movimientos de caja', TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'CAJA_MOVIMIENTOS');

-- Función: PLANES_PAGO (para cuentas por cobrar)
INSERT INTO funciones (nombre, descripcion, activo, fecha_creacion)
SELECT 'PLANES_PAGO', 'Gestión de planes de pago y cuentas por cobrar', TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'PLANES_PAGO');

-- Función: PAGOS_NOMINA (para nómina)
INSERT INTO funciones (nombre, descripcion, activo, fecha_creacion)
SELECT 'PAGOS_NOMINA', 'Gestión de pagos de nómina', TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'PAGOS_NOMINA');

-- Función: REPORTE_CAJA (para reportes)
INSERT INTO funciones (nombre, descripcion, activo, fecha_creacion)
SELECT 'REPORTE_CAJA', 'Generación de reportes de caja', TRUE, NOW()
WHERE NOT EXISTS (SELECT 1 FROM funciones WHERE nombre = 'REPORTE_CAJA');

-- Ahora crear los permisos para cada función con las 4 acciones básicas
-- Asumiendo que las acciones tienen IDs: 1=read, 2=create, 3=update, 4=delete

-- Permisos para CAJA_SESIONES
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre = 'CAJA_SESIONES'
  AND a.nombre IN ('read', 'create', 'update', 'delete')
  AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
  );

-- Permisos para GASTOS
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre = 'GASTOS'
  AND a.nombre IN ('read', 'create', 'update', 'delete')
  AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
  );

-- Permisos para CATEGORIAS_GASTO
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre = 'CATEGORIAS_GASTO'
  AND a.nombre IN ('read', 'create', 'update', 'delete')
  AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
  );

-- Permisos para INGRESOS_VARIOS
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre = 'INGRESOS_VARIOS'
  AND a.nombre IN ('read', 'create', 'update', 'delete')
  AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
  );

-- Permisos para CAJA_MOVIMIENTOS
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre = 'CAJA_MOVIMIENTOS'
  AND a.nombre IN ('read', 'create', 'update', 'delete')
  AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
  );

-- Permisos para PLANES_PAGO
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre = 'PLANES_PAGO'
  AND a.nombre IN ('read', 'create', 'update', 'delete')
  AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
  );

-- Permisos para PAGOS_NOMINA
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre = 'PAGOS_NOMINA'
  AND a.nombre IN ('read', 'create', 'update', 'delete')
  AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
  );

-- Permisos para REPORTE_CAJA
INSERT INTO permisos (funcion_id, accion_id)
SELECT f.id, a.id
FROM funciones f
CROSS JOIN acciones a
WHERE f.nombre = 'REPORTE_CAJA'
  AND a.nombre IN ('read', 'create', 'update', 'delete')
  AND NOT EXISTS (
    SELECT 1 FROM permisos p 
    WHERE p.funcion_id = f.id AND p.accion_id = a.id
  );

-- Verificar los permisos creados
SELECT 
    f.nombre as funcion,
    a.nombre as accion,
    p.id as permiso_id
FROM permisos p
JOIN funciones f ON p.funcion_id = f.id
JOIN acciones a ON p.accion_id = a.id
WHERE f.nombre IN (
    'CAJA_SESIONES', 'GASTOS', 'CATEGORIAS_GASTO', 'INGRESOS_VARIOS',
    'CAJA_MOVIMIENTOS', 'PLANES_PAGO', 'PAGOS_NOMINA', 'REPORTE_CAJA'
)
ORDER BY f.nombre, a.nombre;
