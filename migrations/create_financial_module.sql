-- Financial Module Migration

-- 1. Categorias Gasto
CREATE TABLE IF NOT EXISTS categorias_gasto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Gastos
CREATE TABLE IF NOT EXISTS gastos (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER NOT NULL REFERENCES categorias_gasto(id),
    usuario_id INTEGER REFERENCES usuarios(id),
    monto DECIMAL(10, 2) NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_gasto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comprobante_referencia VARCHAR(100),
    metodo_pago VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Caja Sesiones
CREATE TABLE IF NOT EXISTS caja_sesiones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre TIMESTAMP,
    monto_inicial DECIMAL(10, 2) DEFAULT 0.00,
    monto_final_esperado DECIMAL(10, 2),
    monto_final_real DECIMAL(10, 2),
    diferencia DECIMAL(10, 2),
    estado VARCHAR(20) DEFAULT 'ABIERTA',
    observaciones TEXT
);

-- 4. Caja Movimientos
CREATE TABLE IF NOT EXISTS caja_movimientos (
    id SERIAL PRIMARY KEY,
    sesion_id INTEGER REFERENCES caja_sesiones(id),
    tipo VARCHAR(20) NOT NULL, -- INGRESO, EGRESO
    categoria VARCHAR(50) NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    referencia_tabla VARCHAR(50),
    referencia_id INTEGER,
    usuario_id INTEGER REFERENCES usuarios(id)
);

-- 5. Planes Pago (Cuentas por Cobrar)
CREATE TABLE IF NOT EXISTS planes_pago (
    id SERIAL PRIMARY KEY,
    inscripcion_id INTEGER REFERENCES inscripciones(id) ON DELETE CASCADE,
    inscripcion_paquete_id INTEGER REFERENCES inscripcion_paquete(id) ON DELETE CASCADE,
    estudiante_id INTEGER NOT NULL REFERENCES estudiantes(id),
    monto_total DECIMAL(10, 2) NOT NULL,
    monto_pagado DECIMAL(10, 2) DEFAULT 0.00,
    saldo_pendiente DECIMAL(10, 2) NOT NULL,
    fecha_emision DATE DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE NOT NULL,
    estado VARCHAR(20) DEFAULT 'PENDIENTE',
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Detalle Plan Pago
CREATE TABLE IF NOT EXISTS detalle_plan_pago (
    id SERIAL PRIMARY KEY,
    plan_pago_id INTEGER NOT NULL REFERENCES planes_pago(id) ON DELETE CASCADE,
    monto DECIMAL(10, 2) NOT NULL,
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metodo_pago VARCHAR(50),
    referencia_pago VARCHAR(100),
    usuario_id INTEGER REFERENCES usuarios(id)
);

-- 7. Pagos Nomina
CREATE TABLE IF NOT EXISTS pagos_nomina (
    id SERIAL PRIMARY KEY,
    usuario_empleado_id INTEGER NOT NULL REFERENCES usuarios(id),
    usuario_admin_id INTEGER REFERENCES usuarios(id),
    monto DECIMAL(10, 2) NOT NULL,
    tipo_pago VARCHAR(50) DEFAULT 'SUELDO',
    descripcion TEXT,
    fecha_pago DATE DEFAULT CURRENT_DATE,
    periodo VARCHAR(50),
    metodo_pago VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'PENDIENTE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
