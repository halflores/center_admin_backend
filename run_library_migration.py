from app.db.session import SessionLocal, engine
from app.models.models import Base
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    try:
        db = SessionLocal()
        
        # Read the SQL file
        with open("migrations/create_library_tables.sql", "r") as f:
            sql_script = f.read()
            
        # Execute the SQL script
        logger.info("Executing library tables migration...")
        db.execute(text(sql_script))
        db.commit()
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Error executing migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
