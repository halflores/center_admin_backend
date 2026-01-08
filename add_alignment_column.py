
from sqlalchemy import create_engine, text
from app.core.config import settings

def add_column():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Check if column exists (Postgres specific)
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='dialogue_lines' AND column_name='alignment_json';
            """)
            result = conn.execute(check_sql).fetchone()
            
            if not result:
                print("Adding 'alignment_json' column to 'dialogue_lines' table...")
                alter_sql = text("ALTER TABLE dialogue_lines ADD COLUMN alignment_json TEXT;")
                conn.execute(alter_sql)
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column 'alignment_json' already exists. Skipping.")
                
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_column()
