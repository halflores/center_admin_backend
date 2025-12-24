
import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_empleados_table():
    logger.info("Starting schema fix for 'empleados' table...")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as connection:
            # Rename fecha_ingreso to fecha_contratacion
            try:
                # Check if fecha_ingreso exists first
                result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='empleados' AND column_name='fecha_ingreso';"))
                if result.fetchone():
                    logger.info("Renaming 'fecha_ingreso' to 'fecha_contratacion'...")
                    connection.execute(text("ALTER TABLE empleados RENAME COLUMN fecha_ingreso TO fecha_contratacion;"))
                    logging.info("Column renamed successfully.")
                else:
                    logger.info("'fecha_ingreso' column not found, checking for 'fecha_contratacion'...")
                    result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='empleados' AND column_name='fecha_contratacion';"))
                    if result.fetchone():
                         logger.info("'fecha_contratacion' already exists.")
                    else:
                        logger.error("Neither 'fecha_ingreso' nor 'fecha_contratacion' found!")
                        # Optionally create it if missing?
                        # connection.execute(text("ALTER TABLE empleados ADD COLUMN fecha_contratacion DATE DEFAULT CURRENT_DATE;"))

            except Exception as e:
                logger.error(f"Error renaming column: {e}")

            connection.commit()
            
        logger.info("Schema fix completed.")
        
    except Exception as e:
        logger.error(f"Critical error during schema fix: {e}")

if __name__ == "__main__":
    fix_empleados_table()
