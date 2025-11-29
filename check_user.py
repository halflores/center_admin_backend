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

print("\n=== Usuarios en el sistema ===")
cursor.execute("""
    SELECT u.id, u.correo, u.nombre, u.apellido, r.id as rol_id, r.nombre as rol_nombre
    FROM usuarios u
    LEFT JOIN roles r ON u.rol_id = r.id
    ORDER BY u.id
""")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Email: {row[1]}, Nombre: {row[2]} {row[3]}, Rol ID: {row[4]}, Rol: {row[5]}")

print("\n=== Buscando usuario hal.flores@gmail.com ===")
cursor.execute("""
    SELECT u.id, u.correo, u.nombre, u.apellido, r.id as rol_id, r.nombre as rol_nombre
    FROM usuarios u
    LEFT JOIN roles r ON u.rol_id = r.id
    WHERE u.correo = 'hal.flores@gmail.com'
""")
user = cursor.fetchone()
if user:
    print(f"Usuario encontrado:")
    print(f"  ID: {user[0]}")
    print(f"  Email: {user[1]}")
    print(f"  Nombre: {user[2]} {user[3]}")
    print(f"  Rol ID: {user[4]}")
    print(f"  Rol: {user[5]}")
    
    print(f"\n=== Permisos del usuario (rol_id={user[4]}) ===")
    cursor.execute("""
        SELECT f.nombre as funcion, a.nombre as accion 
        FROM rol_permisos rp 
        JOIN permisos p ON rp.permiso_id = p.id 
        JOIN funciones f ON p.funcion_id = f.id 
        JOIN acciones a ON p.accion_id = a.id 
        WHERE rp.rol_id = %s AND f.nombre IN ('categorias_producto', 'productos')
        ORDER BY f.nombre, a.nombre
    """, (user[4],))
    perms = cursor.fetchall()
    if perms:
        for perm in perms:
            print(f"  {perm[0]}.{perm[1]}")
    else:
        print("  ¡NO TIENE PERMISOS DE INVENTARIO!")
else:
    print("  Usuario NO encontrado")

cursor.close()
conn.close()
