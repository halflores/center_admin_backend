
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

try:
    from app.core.config import settings
    from app.models.models import Estudiante, Inscripcion, Curso, Modulo, InscripcionPaquete, Paquete, ModuloLibro
    
    # Create DB connection
    print(f"DEBUG: Config Database URL: {settings.DATABASE_URL}")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    print("DEBUG: Database connection established.")
    
except Exception as e:
    print(f"CRITICAL: Failed to setup DB connection or imports: {e}")
    sys.exit(1)

ESTUDIANTE_ID = 47

print(f"\nxxx INSPECTING DATA FOR STUDENT {ESTUDIANTE_ID} xxx")

try:
    # 1. Check Student
    est = db.query(Estudiante).filter(Estudiante.id == ESTUDIANTE_ID).first()
    if est:
        print(f"Student Found: {est.nombres} {est.apellidos}")
    else:
        print("Student NOT FOUND!")
        sys.exit(0)

    # 2. Check INSCRIPCION PAQUETE (Priority 1)
    print("\n--- INSC. PAQUETE (New System) ---")
    ips = db.query(InscripcionPaquete).filter(InscripcionPaquete.estudiante_id == ESTUDIANTE_ID).all()
    if not ips:
        print("No InscripcionPaquete records found.")
    for ip in ips:
        print(f"ID: {ip.id} | Estado: '{ip.estado_academico}'")
        if ip.paquete:
            print(f"  -> Paquete: {ip.paquete.nombre} (ID: {ip.paquete.id})")
            if ip.paquete.modulo:
                print(f"  -> Modulo Link: YES (ID: {ip.paquete.modulo_id}) - {ip.paquete.modulo.nombre}")
            else:
                print(f"  -> Modulo Link: NO (modulo_id: {ip.paquete.modulo_id})")
        else:
            print("  -> Paquete: None")

    # 3. Check INSCRIPCION (Priority 2 - Fallback)
    print("\n--- INSCRIPCION (Old System) ---")
    inscriptions = db.query(Inscripcion).filter(Inscripcion.estudiante_id == ESTUDIANTE_ID).all()
    if not inscriptions:
        print("No Inscripcion records found.")
    for ins in inscriptions:
        print(f"ID: {ins.id} | Estado: '{ins.estado}' | CursoID: {ins.curso_id}")
        if ins.curso:
            print(f"  -> Curso ID: {ins.curso.id}") # Curso has no 'nombre' apparently
            if ins.curso.modulo:
                print(f"     -> Modulo Link: YES (ID: {ins.curso.modulo_id}) - {ins.curso.modulo.nombre}")
            else:
                print(f"     -> Modulo Link: NO (modulo_id: {ins.curso.modulo_id})")
        else:
            print("  -> Curso: None")
            
    # 4. Check Books for Module 1 (Active)
    TARGET_MODULO_ID = 1
    print(f"\n--- BOOKS FOR MODULE {TARGET_MODULO_ID} ---")
    books = db.query(ModuloLibro).filter(
        ModuloLibro.modulo_id == TARGET_MODULO_ID,
        ModuloLibro.activo == True
    ).all()
    print(f"Found {len(books)} active book associations.")
    for b in books:
        # Check if Libro exists
        if b.libro:
            # Check availability logic
            disponible = b.libro.cantidad_disponible > 0
            print(f"  - Libro ID: {b.libro_id} | Titulo: {b.libro.titulo} | Disp: {b.libro.cantidad_disponible} (>0? {disponible})")
        else:
            print(f"  - Libro ID: {b.libro_id} | Libro Object MISSING (Foreign Key issue?)")

    # 5. Check MODULOS Table (Why is API returning 0?)
    print(f"\n--- CHECKING MODULOS TABLE ---")
    all_modulos = db.query(Modulo).all()
    print(f"Total Modulos found: {len(all_modulos)}")
    for m in all_modulos:
        print(f"ID: {m.id} | Nombre: {m.nombre} | Activo: {m.activo} (Type: {type(m.activo)})")

except Exception as e:
    print(f"ERROR during inspection: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
    print("\nxxx END INSPECTION xxx")
