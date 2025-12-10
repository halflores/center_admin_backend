from sqlalchemy import create_engine, inspect
from app.core.config import settings

try:
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('profesores')]
    print(f"Columns in profesores table: {columns}")
    
    if 'nivel_formacion_id' not in columns:
        print("MISSING: nivel_formacion_id")
    if 'comentarios' not in columns:
        print("MISSING: comentarios")
        
    if not inspector.has_table('niveles_formacion'):
        print("MISSING TABLE: niveles_formacion")
        
except Exception as e:
    print(f"Error connecting to DB: {e}")
