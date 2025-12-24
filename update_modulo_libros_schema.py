"""
Script para actualizar el esquema de la tabla modulo_libros
Agrega soporte para clasificación de libros (obligatorio/recomendado)
y préstamos extracurriculares
"""
import psycopg2
from dotenv import load_dotenv
import os
import sys

# Cargar variables de entorno
load_dotenv()

def update_schema():
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'institute_lms'),
            user=os.getenv('DB_USER', 'admin'),
            password=os.getenv('DB_PASSWORD')
        )
        
        cursor = conn.cursor()
        
        print("Conectado a la base de datos exitosamente")
        
        # 1. Verificar si la tabla modulo_libros existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'modulo_libros'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("⚠️  La tabla modulo_libros no existe. Creándola...")
            cursor.execute("""
                CREATE TABLE modulo_libros (
                    id SERIAL PRIMARY KEY,
                    modulo_id INTEGER REFERENCES modulos(id) ON DELETE CASCADE,
                    libro_id INTEGER REFERENCES libros(id) ON DELETE CASCADE,
                    tipo_asignacion VARCHAR(20) DEFAULT 'recomendado' 
                        CHECK (tipo_asignacion IN ('obligatorio', 'recomendado')),
                    activo BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(modulo_id, libro_id)
                );
            """)
            print("✅ Tabla modulo_libros creada")
        else:
            print("✅ Tabla modulo_libros ya existe")
            
            # Agregar columna tipo_asignacion si no existe
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'modulo_libros' AND column_name = 'tipo_asignacion';
            """)
            if not cursor.fetchone():
                print("Agregando columna tipo_asignacion...")
                cursor.execute("""
                    ALTER TABLE modulo_libros 
                    ADD COLUMN tipo_asignacion VARCHAR(20) DEFAULT 'recomendado'
                    CHECK (tipo_asignacion IN ('obligatorio', 'recomendado'));
                """)
                print("✅ Columna tipo_asignacion agregada")
            else:
                print("✅ Columna tipo_asignacion ya existe")
            
            # Agregar columna activo si no existe
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'modulo_libros' AND column_name = 'activo';
            """)
            if not cursor.fetchone():
                print("Agregando columna activo...")
                cursor.execute("""
                    ALTER TABLE modulo_libros 
                    ADD COLUMN activo BOOLEAN DEFAULT TRUE;
                """)
                print("✅ Columna activo agregada")
            else:
                print("✅ Columna activo ya existe")
            
            # Agregar timestamps si no existen
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'modulo_libros' AND column_name = 'created_at';
            """)
            if not cursor.fetchone():
                print("Agregando columnas de timestamp...")
                cursor.execute("""
                    ALTER TABLE modulo_libros 
                    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                """)
                print("✅ Columnas de timestamp agregadas")
            else:
                print("✅ Columnas de timestamp ya existen")
        
        # 2. Crear índices para modulo_libros
        print("\nCreando índices para modulo_libros...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_modulo_libros_modulo 
            ON modulo_libros(modulo_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_modulo_libros_libro 
            ON modulo_libros(libro_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_modulo_libros_tipo 
            ON modulo_libros(tipo_asignacion);
        """)
        print("✅ Índices creados")
        
        # 3. Actualizar tabla prestamos
        print("\nActualizando tabla prestamos...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'prestamos' AND column_name = 'es_extracurricular';
        """)
        if not cursor.fetchone():
            print("Agregando columna es_extracurricular...")
            cursor.execute("""
                ALTER TABLE prestamos 
                ADD COLUMN es_extracurricular BOOLEAN DEFAULT FALSE;
            """)
            print("✅ Columna es_extracurricular agregada a prestamos")
        else:
            print("✅ Columna es_extracurricular ya existe en prestamos")
        
        # Commit de todos los cambios
        conn.commit()
        
        # Mostrar estructura final
        print("\n" + "="*60)
        print("ESTRUCTURA FINAL DE modulo_libros:")
        print("="*60)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'modulo_libros'
            ORDER BY ordinal_position;
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]:<20} {row[1]:<15} NULL: {row[2]:<5} DEFAULT: {row[3]}")
        
        print("\n" + "="*60)
        print("✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_schema()
