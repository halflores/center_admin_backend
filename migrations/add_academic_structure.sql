-- Academic Structure Migration
-- Generated for Institute LMS

-- =====================================================
-- PROGRAMAS (Academic Programs)
-- =====================================================
CREATE TABLE IF NOT EXISTS programas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- NIVELES (Academic Levels like A1, A2, B1, etc.)
-- =====================================================
CREATE TABLE IF NOT EXISTS niveles (
    id SERIAL PRIMARY KEY,
    programa_id INTEGER NOT NULL REFERENCES programas(id) ON DELETE CASCADE,
    codigo VARCHAR(20),
    nombre VARCHAR(100) NOT NULL,
    nombre_comercial VARCHAR(100),
    orden INTEGER DEFAULT 0,
    duracion_sugerida VARCHAR(50),
    enfoque_principal TEXT,
    duracion_meses INTEGER,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_niveles_programa ON niveles(programa_id);

-- =====================================================
-- MODULOS (Modules/Subjects within levels)
-- =====================================================
CREATE TABLE IF NOT EXISTS modulos (
    id SERIAL PRIMARY KEY,
    nivel_id INTEGER NOT NULL REFERENCES niveles(id) ON DELETE CASCADE,
    codigo VARCHAR(20),
    nombre VARCHAR(150) NOT NULL,
    duracion_semanas INTEGER,
    horas_presenciales INTEGER,
    horas_totales INTEGER,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_modulos_nivel ON modulos(nivel_id);

-- =====================================================
-- PROFESORES (Teachers)
-- =====================================================
CREATE TABLE IF NOT EXISTS profesores (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    ci VARCHAR(20) UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    sexo VARCHAR(20),
    direccion VARCHAR(255),
    celular VARCHAR(20),
    correo VARCHAR(150),
    titulo_academico VARCHAR(100),
    especialidad VARCHAR(100),
    nivel_formacion VARCHAR(50),
    experiencia_anios INTEGER,
    fecha_ingreso DATE,
    fecha_salida DATE,
    tipo_contrato VARCHAR(50),
    salario_hora NUMERIC(10, 2),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_profesores_usuario ON profesores(usuario_id);

-- =====================================================
-- PROFESOR_CAMPUS (Many-to-Many: Profesor <-> Campus)
-- =====================================================
CREATE TABLE IF NOT EXISTS profesor_campus (
    profesor_id INTEGER NOT NULL REFERENCES profesores(id) ON DELETE CASCADE,
    campus_id INTEGER NOT NULL REFERENCES campus(id) ON DELETE CASCADE,
    principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (profesor_id, campus_id)
);

-- =====================================================
-- CURSOS (Course offerings)
-- =====================================================
CREATE TABLE IF NOT EXISTS cursos (
    id SERIAL PRIMARY KEY,
    modulo_id INTEGER NOT NULL REFERENCES modulos(id) ON DELETE CASCADE,
    profesor_id INTEGER REFERENCES profesores(id),
    campus_id INTEGER REFERENCES campus(id),
    fecha_inicio DATE,
    fecha_fin DATE,
    cupo_maximo INTEGER,
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cursos_modulo ON cursos(modulo_id);
CREATE INDEX IF NOT EXISTS idx_cursos_profesor ON cursos(profesor_id);
CREATE INDEX IF NOT EXISTS idx_cursos_campus ON cursos(campus_id);

-- =====================================================
-- HORARIOS (Class schedules)
-- =====================================================
CREATE TABLE IF NOT EXISTS horarios (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    dia_semana VARCHAR(20) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    aula VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_horarios_curso ON horarios(curso_id);

-- =====================================================
-- INSCRIPCIONES (Student enrollments)
-- =====================================================
CREATE TABLE IF NOT EXISTS inscripciones (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    curso_id INTEGER NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    gestion_id INTEGER NOT NULL REFERENCES gestion(id),
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    monto_pagado NUMERIC(10, 2),
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_inscripcion UNIQUE (estudiante_id, curso_id, gestion_id)
);

CREATE INDEX IF NOT EXISTS idx_inscripciones_estudiante ON inscripciones(estudiante_id);
CREATE INDEX IF NOT EXISTS idx_inscripciones_curso ON inscripciones(curso_id);
CREATE INDEX IF NOT EXISTS idx_inscripciones_gestion ON inscripciones(gestion_id);

-- =====================================================
-- PAGOS_PROFESOR (Teacher payments)
-- =====================================================
CREATE TABLE IF NOT EXISTS pagos_profesor (
    id SERIAL PRIMARY KEY,
    profesor_id INTEGER NOT NULL REFERENCES profesores(id) ON DELETE CASCADE,
    gestion_id INTEGER REFERENCES gestion(id),
    periodo VARCHAR(50),
    horas_trabajadas INTEGER,
    monto_hora NUMERIC(10, 2),
    monto_total NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'PENDIENTE',
    fecha_pago DATE,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pagos_profesor ON pagos_profesor(profesor_id);
CREATE INDEX IF NOT EXISTS idx_pagos_gestion ON pagos_profesor(gestion_id);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================
COMMENT ON TABLE programas IS 'Academic programs (e.g., Adults, Kids)';
COMMENT ON TABLE niveles IS 'Academic levels within programs (e.g., A1, A2, B1, 1 Básico)';
COMMENT ON TABLE modulos IS 'Modules/subjects within levels (e.g., Foundations, My World)';
COMMENT ON TABLE profesores IS 'Teachers with personal and professional information';
COMMENT ON TABLE profesor_campus IS 'Many-to-many relationship between teachers and campuses';
COMMENT ON TABLE cursos IS 'Course offerings linking modules with teachers and campuses';
COMMENT ON TABLE horarios IS 'Weekly schedules for courses';
COMMENT ON TABLE inscripciones IS 'Student enrollments in courses per academic period';
COMMENT ON TABLE pagos_profesor IS 'Payment records for teachers';
