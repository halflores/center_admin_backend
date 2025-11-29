import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "institute_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "07.Hector")

# SQL Script Path
SQL_FILE_PATH = r"e:\INSTITUTE\institute_lms\center_admin_frontend\setup_inventory_permissions.sql"

def run_sql_script():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print(f"Connected to database: {DB_NAME}")

        # Read the SQL script
        with open(SQL_FILE_PATH, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        print(f"Executing SQL script from: {SQL_FILE_PATH}")
        
        # Execute the script
        cursor.execute(sql_script)
        
        print("SQL script executed successfully.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error executing script: {e}")

if __name__ == "__main__":
    run_sql_script()
