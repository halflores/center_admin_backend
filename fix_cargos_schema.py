
import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_cargos_table():
    logger.info("Starting schema fix for 'cargos' table...")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as connection:
            # 1. Add salario_base column
            try:
                logger.info("Adding 'salario_base' column...")
                connection.execute(text("ALTER TABLE cargos ADD COLUMN IF NOT EXISTS salario_base NUMERIC(10, 2);"))
                logging.info("'salario_base' column added successfully.")
            except Exception as e:
                logger.error(f"Error adding 'salario_base': {e}")

            # 2. Add updated_at column
            try:
                logger.info("Adding 'updated_at' column...")
                connection.execute(text("ALTER TABLE cargos ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
                logging.info("'updated_at' column added successfully.")
            except Exception as e:
                logger.error(f"Error adding 'updated_at': {e}")

            connection.commit()
            
        logger.info("Schema fix completed.")
        
    except Exception as e:
        logger.error(f"Critical error during schema fix: {e}")

if __name__ == "__main__":
    fix_cargos_table()
