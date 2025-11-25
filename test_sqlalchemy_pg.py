try:
    from sqlalchemy.dialects.postgresql import psycopg2
    print("Successfully imported sqlalchemy.dialects.postgresql.psycopg2")
    
    import psycopg2
    print(f"psycopg2 version: {psycopg2.__version__}")
except ImportError as e:
    print(f"Error importing: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
