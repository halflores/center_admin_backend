import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def grant_biblioteca_permissions():
    """Grant biblioteca permissions to role ID 6"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("🔄 Otorgando permisos de biblioteca al Rol ID 6...")
        
        # Read and execute SQL file
        with open('migrations/grant_biblioteca_permissions_rol6.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        cursor.execute(sql_script)
        conn.commit()
        
        print("✅ Permisos otorgados exitosamente!")
        print("\nPermisos otorgados para las siguientes funciones:")
        print("  - biblioteca (general)")
        print("  - libros")
        print("  - prestamos")
        print("  - multas")
        print("  - reservas")
        print("  - generos_literarios")
        print("  - editoriales")
        print("  - autores")
        print("\nAcciones: read, create, update, delete")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al otorgar permisos: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    grant_biblioteca_permissions()
