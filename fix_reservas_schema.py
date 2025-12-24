
import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_reservas_table():
    logger.info("Starting schema fix for 'reservas' table...")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as connection:
            # 1. Add usuario_id column
            try:
                logger.info("Adding 'usuario_id' column...")
                connection.execute(text("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS usuario_id INTEGER REFERENCES usuarios(id);"))
                logging.info("'usuario_id' column added successfully.")
            except Exception as e:
                logger.error(f"Error adding 'usuario_id': {e}")

            # 2. Add fecha_notificacion column
            try:
                logger.info("Adding 'fecha_notificacion' column...")
                connection.execute(text("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS fecha_notificacion TIMESTAMP;"))
                logging.info("'fecha_notificacion' column added successfully.")
            except Exception as e:
                logger.error(f"Error adding 'fecha_notificacion': {e}")

            # 3. Alter fecha_expiracion to be NULLABLE (match model)
            try:
                logger.info("Altering 'fecha_expiracion' to be nullable...")
                connection.execute(text("ALTER TABLE reservas ALTER COLUMN fecha_expiracion DROP NOT NULL;"))
                logging.info("'fecha_expiracion' altered successfully.")
            except Exception as e:
                logger.error(f"Error altering 'fecha_expiracion': {e}")
                
            connection.commit()
            
        logger.info("Schema fix completed.")
        
    except Exception as e:
        logger.error(f"Critical error during schema fix: {e}")

if __name__ == "__main__":
    fix_reservas_table()
