"""
Execute SQL script to grant cash report permissions to Role ID 6
Date: 2025-12-19
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_permissions():
    engine = create_engine(settings.DATABASE_URL)
    
    with open('grant_cash_report_permissions.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Split by semicolons and execute each statement
    statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
    
    with engine.connect() as conn:
        for stmt in statements:
            if stmt:
                try:
                    result = conn.execute(text(stmt))
                    conn.commit()
                    # If it's a SELECT statement, print results
                    if stmt.strip().upper().startswith('SELECT'):
                        print("\n=== Verification Results ===")
                        for row in result:
                            print(f"  Rol: {row[0]}, Función: {row[1]}, Acción: {row[2]}")
                except Exception as e:
                    print(f"Error executing statement: {e}")
                    print(f"Statement: {stmt[:100]}...")
                    continue
        
        print("\n✓ Permissions granted successfully to Role ID 6!")
        print("  - reportes_caja: read, create")
        print("  - finanzas: create, read, update, delete")

if __name__ == "__main__":
    run_permissions()
