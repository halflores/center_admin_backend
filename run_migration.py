from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        with connection.begin():
            # Add column
            try:
                connection.execute(text("ALTER TABLE carrito_compras ADD COLUMN IF NOT EXISTS descuento NUMERIC(10, 2) DEFAULT 0.0;"))
                print("Column 'descuento' added or already exists.")
            except Exception as e:
                print(f"Error adding column: {e}")

            # Update existing records
            try:
                connection.execute(text("UPDATE carrito_compras SET descuento = 0.0 WHERE descuento IS NULL;"))
                print("Existing records updated.")
            except Exception as e:
                print(f"Error updating records: {e}")

if __name__ == "__main__":
    run_migration()
