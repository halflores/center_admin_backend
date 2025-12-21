-- Create generos_literarios table
CREATE TABLE IF NOT EXISTS generos_literarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create editoriales table
CREATE TABLE IF NOT EXISTS editoriales (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    pais VARCHAR(100),
    sitio_web VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create autores table
CREATE TABLE IF NOT EXISTS autores (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    nacionalidad VARCHAR(100),
    biografia TEXT,
    fecha_nacimiento DATE,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create libros table
CREATE TABLE IF NOT EXISTS libros (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    subtitulo VARCHAR(255),
    genero_id INTEGER NOT NULL REFERENCES generos_literarios(id),
    editorial_id INTEGER NOT NULL REFERENCES editoriales(id),
    anio_publicacion INTEGER,
    numero_paginas INTEGER,
    idioma VARCHAR(50) DEFAULT 'Español',
    cantidad_total INTEGER NOT NULL DEFAULT 1,
    cantidad_disponible INTEGER NOT NULL DEFAULT 1,
    ubicacion_fisica VARCHAR(100),
    descripcion TEXT,
    imagen_portada VARCHAR(255),
    estado VARCHAR(20) DEFAULT 'DISPONIBLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for libros
CREATE INDEX IF NOT EXISTS idx_libros_isbn ON libros(isbn);
CREATE INDEX IF NOT EXISTS idx_libros_titulo ON libros(titulo);

-- Create libro_autores table (Many-to-Many)
CREATE TABLE IF NOT EXISTS libro_autores (
    id SERIAL PRIMARY KEY,
    libro_id INTEGER NOT NULL REFERENCES libros(id) ON DELETE CASCADE,
    autor_id INTEGER NOT NULL REFERENCES autores(id),
    orden INTEGER DEFAULT 1
);

-- Create prestamos table
CREATE TABLE IF NOT EXISTS prestamos (
    id SERIAL PRIMARY KEY,
    libro_id INTEGER NOT NULL REFERENCES libros(id),
    estudiante_id INTEGER REFERENCES estudiantes(id),
    profesor_id INTEGER REFERENCES profesores(id),
    usuario_registro_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha_prestamo DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_devolucion_esperada DATE NOT NULL,
    fecha_devolucion_real DATE,
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    observaciones TEXT,
    multa NUMERIC(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reservas table
CREATE TABLE IF NOT EXISTS reservas (
    id SERIAL PRIMARY KEY,
    libro_id INTEGER NOT NULL REFERENCES libros(id),
    estudiante_id INTEGER REFERENCES estudiantes(id),
    profesor_id INTEGER REFERENCES profesores(id),
    fecha_reserva DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_expiracion DATE NOT NULL,
    estado VARCHAR(20) DEFAULT 'PENDIENTE',
    notificado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
