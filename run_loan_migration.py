import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Run the loan system migration"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("🔄 Running loan system migration...")
        
        # Read and execute migration file
        with open('migrations/add_loan_system_features.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print("\nChanges applied:")
        print("  - Added loan type column to prestamos")
        print("  - Added late fee tracking columns")
        print("  - Created multas_prestamo table")
        print("  - Created modulo_libros table")
        print("  - Added indexes for performance")
        print("  - Created trigger for automatic late fee calculation")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    run_migration()
