import sqlite3
from contextlib import closing

DATABASE_PATH = 'path_to_your_database.db'  # Update this to your actual database path

def get_connection():
    """Establishes a connection to the database and returns the connection object."""
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def execute_query(query, params=None):
    """Executes a given SQL query with optional parameters."""
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.fetchall()

def initialize_database():
    """Initializes the database by executing the schema.sql file."""
    with open('schema.sql', 'r') as f:
        schema = f.read()
    execute_query(schema)

# Additional functions can be added here as needed