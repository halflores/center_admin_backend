"""
Migración: Crear tablas para Audio Lessons
==========================================

Este script crea las tablas necesarias para el módulo de lecciones
de audio con sincronización de texto.

Ejecutar: python migrations/create_audio_lessons_tables.py
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine, SessionLocal
from app.core.config import settings


def run_migration():
    """Ejecuta la migración para crear las tablas de audio lessons."""
    
    print("=" * 60)
    print("MIGRACIÓN: Crear tablas para Audio Lessons")
    print("=" * 60)
    print(f"Base de datos: {settings.DB_NAME}")
    print()
    
    # SQL para crear las tablas
    sql_statements = [
        # Tabla principal de lecciones de audio
        """
        CREATE TABLE IF NOT EXISTS audio_lessons (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            descripcion TEXT,
            
            -- Relaciones académicas
            modulo_id INTEGER REFERENCES modulos(id) ON DELETE SET NULL,
            curso_id INTEGER REFERENCES cursos(id) ON DELETE SET NULL,
            
            -- Archivo de audio
            audio_url VARCHAR(500),
            audio_duration_ms INTEGER,
            
            -- Contenido de texto
            transcript_text TEXT NOT NULL,
            
            -- Timestamps generados por Gentle (JSON)
            timestamps_json TEXT,
            
            -- Estado del procesamiento
            estado VARCHAR(20) DEFAULT 'PENDIENTE',
            
            -- Metadatos
            orden INTEGER DEFAULT 0,
            activo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        
        # Índices para audio_lessons
        """
        CREATE INDEX IF NOT EXISTS idx_audio_lessons_modulo 
        ON audio_lessons(modulo_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_audio_lessons_curso 
        ON audio_lessons(curso_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_audio_lessons_estado 
        ON audio_lessons(estado);
        """,
        
        # Tabla de progreso del estudiante
        """
        CREATE TABLE IF NOT EXISTS student_audio_progress (
            id SERIAL PRIMARY KEY,
            estudiante_id INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
            audio_lesson_id INTEGER NOT NULL REFERENCES audio_lessons(id) ON DELETE CASCADE,
            
            -- Progreso
            last_position_ms INTEGER DEFAULT 0,
            times_completed INTEGER DEFAULT 0,
            total_time_listened_ms INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT FALSE,
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Constraint único
            CONSTRAINT unique_student_audio_progress 
            UNIQUE (estudiante_id, audio_lesson_id)
        );
        """,
        
        # Índices para student_audio_progress
        """
        CREATE INDEX IF NOT EXISTS idx_student_audio_progress_estudiante 
        ON student_audio_progress(estudiante_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_student_audio_progress_lesson 
        ON student_audio_progress(audio_lesson_id);
        """,
        
        # Comentarios en las tablas
        """
        COMMENT ON TABLE audio_lessons IS 
        'Lecciones de audio con sincronización de texto para estudiantes';
        """,
        
        """
        COMMENT ON COLUMN audio_lessons.timestamps_json IS 
        'JSON con timestamps por palabra: {"words": [{"word": "Hello", "start": 0, "end": 450}], "duration_ms": 5000}';
        """,
        
        """
        COMMENT ON TABLE student_audio_progress IS 
        'Tracking del progreso de estudiantes en lecciones de audio';
        """,
    ]
    
    # Ejecutar migración
    with engine.connect() as connection:
        for i, sql in enumerate(sql_statements, 1):
            try:
                connection.execute(text(sql))
                connection.commit()
                print(f"✓ Statement {i}/{len(sql_statements)} ejecutado correctamente")
            except Exception as e:
                print(f"✗ Error en statement {i}: {e}")
                # Continuar con los demás statements
    
    print()
    print("=" * 60)
    print("✓ Migración completada")
    print("=" * 60)
    
    # Verificar tablas creadas
    verify_tables()


def verify_tables():
    """Verifica que las tablas se crearon correctamente."""
    print()
    print("Verificando tablas creadas...")
    
    with engine.connect() as connection:
        # Verificar audio_lessons
        result = connection.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'audio_lessons'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        
        if columns:
            print()
            print("Tabla 'audio_lessons':")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        else:
            print("  ✗ Tabla 'audio_lessons' no encontrada")
        
        # Verificar student_audio_progress
        result = connection.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'student_audio_progress'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        
        if columns:
            print()
            print("Tabla 'student_audio_progress':")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        else:
            print("  ✗ Tabla 'student_audio_progress' no encontrada")


def drop_tables():
    """Elimina las tablas (para desarrollo/testing)."""
    print("ADVERTENCIA: Esto eliminará las tablas de audio lessons!")
    confirm = input("¿Continuar? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Cancelado.")
        return
    
    sql_statements = [
        "DROP TABLE IF EXISTS student_audio_progress CASCADE;",
        "DROP TABLE IF EXISTS audio_lessons CASCADE;",
    ]
    
    with engine.connect() as connection:
        for sql in sql_statements:
            connection.execute(text(sql))
            connection.commit()
            print(f"✓ Ejecutado: {sql}")
    
    print("Tablas eliminadas.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        drop_tables()
    else:
        run_migration()
