import sys
import os
from sqlalchemy import create_engine, inspect

# Add the parent directory to sys.path
sys.path.append(os.getcwd())

from app.core.config import settings

def check_arqueo_schema():
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    if 'caja_arqueos' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('caja_arqueos')]
        print(f"Columns in caja_arqueos table: {columns}")
    else:
        print("Table caja_arqueos does not exist.")

if __name__ == "__main__":
    check_arqueo_schema()
