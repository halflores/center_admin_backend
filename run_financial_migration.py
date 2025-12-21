from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    print("Starting Financial Module Migration...")
    engine = create_engine(settings.DATABASE_URL)
    
    with open("migrations/create_financial_module.sql", "r") as f:
        sql_content = f.read()

    # Split by statements implies usually splitting by ';' but let's see if we can execute the whole block or need splitting.
    # Usually execute() can take a block if the driver supports it, or we iterate.
    # The simpler approach for DDL in postgres with sqlalchemy is often just one go or statement by statement.
    # Let's try executing the whole block first as psycopg2 usually handles multiple statements in one execute call or we can split.
    # Given the file has comments and multiple CREATE TABLE, splitting by ';' might be safer or just rely on the driver.
    # I'll try to split to be safe and give progress updates.
    
    statements = sql_content.split(';')
    
    with engine.connect() as connection:
        with connection.begin():
            for statement in statements:
                if statement.strip():
                    try:
                        stmt_preview = statement[:50].strip().replace('\n', ' ')
                        print(f"Executing: {stmt_preview}...")
                        connection.execute(text(statement))
                    except Exception as e:
                        print(f"Error executing statement: {e}")
                        raise e
            print("Migration completed successfully.")

if __name__ == "__main__":
    run_migration()
