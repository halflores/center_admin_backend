try:
    import psycopg2
    print(f"psycopg2 version: {psycopg2.__version__}")
    print(f"psycopg2 location: {psycopg2.__file__}")
except ImportError as e:
    print(f"Error importing psycopg2: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
