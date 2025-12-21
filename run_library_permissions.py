from app.db.session import SessionLocal, engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_permissions():
    try:
        db = SessionLocal()
        
        # Read the SQL file
        with open("migrations/library_permissions.sql", "r") as f:
            sql_script = f.read()
            
        # Execute the SQL script
        logger.info("Executing library permissions script...")
        db.execute(text(sql_script))
        db.commit()
        logger.info("Permissions granted successfully!")
        
    except Exception as e:
        logger.error(f"Error executing permissions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_permissions()
