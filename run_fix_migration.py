import sys
import os
from sqlalchemy import create_engine, text

# Add the parent directory to sys.path
sys.path.append(os.getcwd())

from app.core.config import settings

def run_migration():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        with open("add_missing_columns.sql", "r") as f:
            sql = f.read()
            connection.execute(text(sql))
            connection.commit()
            print("Migration executed successfully.")

if __name__ == "__main__":
    run_migration()
