from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import Profesor, NivelFormacion

try:
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    print("Querying NivelesFormacion...")
    niveles = db.query(NivelFormacion).all()
    print(f"Found {len(niveles)} niveles")
    for n in niveles:
        print(f"- {n.nombre}")
        
    print("\nQuerying Profesores...")
    profesores = db.query(Profesor).limit(5).all()
    print(f"Found {len(profesores)} profesores (limit 5)")
    for p in profesores:
        print(f"- {p.nombres} {p.apellidos} (Nivel ID: {p.nivel_formacion_id})")
        
    db.close()
    print("\nQueries successful.")
except Exception as e:
    print(f"\nError executing queries: {e}")
