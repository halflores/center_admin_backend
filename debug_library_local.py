
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import InscripcionPaquete, Paquete, Inscripcion, Modulo, ModuloLibro, Libro, Estudiante, Curso
from app.core.config import settings

# Setup DB connection
# Assuming the user is running docker, the DB might be exposed on localhost:3306 or similar.
# If this fails, I might need to ask the user for the connection string or try to infer it.
# However, usually the app runs inside docker. 
# Trying to run this script might fail if deps are not installed locally.

# But wait, looking at the user's workspace "e:\INSTITUTE\..." 
# The user seems to be editing files on Windows. 
# The backend is likely python.

import sys
sys.path.append('.') # Add current dir to path

# Mock settings just in case or try to import
try:
    from app.session import SessionLocal
    db = SessionLocal()
    print("Database connection successful via App Session")
except Exception as e:
    print(f"Could not connect via App Session: {e}")
    # Fallback to a common local connection string if known, else exit
    # Try connecting to localhost assuming standard port
    DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/institute_lms" # Example
    # But I don't know the password. I should rely on existing code.
    print("Exiting as I cannot connect to DB without config.")
    sys.exit(1)

estudiante_id = 47

print(f"--- Debugging Student {estudiante_id} ---")

# 1. Check InscripcionPaquete
ins_paq = db.query(InscripcionPaquete).filter(
    InscripcionPaquete.estudiante_id == estudiante_id
).all()

print(f"Found {len(ins_paq)} InscripcionPaquete records.")
for ip in ins_paq:
    print(f"IP ID: {ip.id}, Estado: {ip.estado_academico}, PaqueteID: {ip.paquete_id}")
    if ip.paquete:
        print(f"  -> Paquete: {ip.paquete.nombre}, ModuloID: {ip.paquete.modulo_id}")

# 2. Check Inscripcion (Old)
ins_old = db.query(Inscripcion).filter(
    Inscripcion.estudiante_id == estudiante_id
).all()

print(f"Found {len(ins_old)} Inscripcion records.")
for i in ins_old:
    print(f"INS ID: {i.id}, Estado: {i.estado}, CursoID: {i.curso_id}")
    if i.curso:
         print(f"  -> Curso: {i.curso.id}, ModuloID: {i.curso.modulo_id}")

# 3. Test the exact query causing issues
try:
    # Copy paste the query from library_service.py
    inscripcion_paquete = db.query(InscripcionPaquete).join(Paquete).filter(
            InscripcionPaquete.estudiante_id == estudiante_id,
            InscripcionPaquete.estado_academico.in_(['INSCRITO', 'Inscrito', 'inscrito'])
        ).order_by(InscripcionPaquete.fecha_inscripcion.desc()).first()
    
    print("Query InscripcionPaquete execution: SUCCESS")
    if inscripcion_paquete:
        print(f"Active IP found: {inscripcion_paquete.id}")
    else:
        print("No Active IP found via query.")
        
except Exception as e:
    print(f"Query InscripcionPaquete FAILED: {e}")
    import traceback
    traceback.print_exc()

print("--- End Debug ---")
