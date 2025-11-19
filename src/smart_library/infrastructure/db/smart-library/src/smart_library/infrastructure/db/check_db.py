def check_database_connection():
    import psycopg2
    from psycopg2 import sql
    from src.smart_library.infrastructure.db.db import get_connection

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def validate_schema():
    # Placeholder for schema validation logic
    pass

if __name__ == "__main__":
    if check_database_connection():
        print("Database connection is successful.")
    else:
        print("Database connection failed.")