from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    engine = create_engine(settings.DATABASE_URL)
    connection = engine.connect()
    try:
        with open("migrations/add_category_permissions.sql", "r", encoding="utf-8") as file:
            sql_script = file.read()
            
        print("Executing permission migration...")
        connection.execute(text(sql_script))
        connection.commit()
        print("Migration successful: Permissions added.")
        
    except Exception as e:
        print(f"Error executing migration: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    run_migration()
