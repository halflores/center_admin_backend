
import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_empleados_genero():
    logger.info("Starting schema fix for 'empleados' table (adding genero)...")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as connection:
            # Add genero column
            try:
                logger.info("Adding 'genero' column...")
                connection.execute(text("ALTER TABLE empleados ADD COLUMN IF NOT EXISTS genero VARCHAR(10);"))
                logging.info("'genero' column added successfully.")
            except Exception as e:
                logger.error(f"Error adding 'genero': {e}")

            connection.commit()
            
        logger.info("Schema fix completed.")
        
    except Exception as e:
        logger.error(f"Critical error during schema fix: {e}")

if __name__ == "__main__":
    fix_empleados_genero()
