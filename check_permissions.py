import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "institute_db"),
    user=os.getenv("DB_USER", "admin"),
    password=os.getenv("DB_PASSWORD", "07.Hector")
)

cursor = conn.cursor()

print("\n=== Permisos creados para inventario ===")
cursor.execute("""
    SELECT f.nombre as funcion, a.nombre as accion 
    FROM permisos p 
    JOIN funciones f ON p.funcion_id = f.id 
    JOIN acciones a ON p.accion_id = a.id 
    WHERE f.nombre IN ('categorias_producto', 'productos') 
    ORDER BY f.nombre, a.nombre
""")
for row in cursor.fetchall():
    print(f"  {row[0]}.{row[1]}")

print("\n=== Permisos asignados al rol 6 (inventario) ===")
cursor.execute("""
    SELECT r.nombre, f.nombre as funcion, a.nombre as accion 
    FROM rol_permisos rp 
    JOIN roles r ON rp.rol_id = r.id 
    JOIN permisos p ON rp.permiso_id = p.id 
    JOIN funciones f ON p.funcion_id = f.id 
    JOIN acciones a ON p.accion_id = a.id 
    WHERE r.id = 6 AND f.nombre IN ('categorias_producto', 'productos') 
    ORDER BY f.nombre, a.nombre
""")
results = cursor.fetchall()
if results:
    for row in results:
        print(f"  {row[0]}: {row[1]}.{row[2]}")
else:
    print("  ¡NO HAY PERMISOS ASIGNADOS!")

cursor.close()
conn.close()
