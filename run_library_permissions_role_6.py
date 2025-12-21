from app.db.session import SessionLocal, engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_permissions_role_6():
    try:
        db = SessionLocal()
        
        # Read the SQL file
        with open("migrations/grant_library_permissions_role_6.sql", "r") as f:
            sql_script = f.read()
            
        # Execute the SQL script
        logger.info("Executing library permissions script for role 6...")
        db.execute(text(sql_script))
        db.commit()
        logger.info("Permissions granted to role 6 successfully!")
        
    except Exception as e:
        logger.error(f"Error executing permissions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_permissions_role_6()
