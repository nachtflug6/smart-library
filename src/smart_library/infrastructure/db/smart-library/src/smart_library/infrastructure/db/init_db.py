def get_connection():
    import sqlite3  # or your preferred database library
    from pathlib import Path

    # Define the path to the database file
    db_file = Path(__file__).resolve().parent / 'database.db'  # Adjust the database file name as needed

    # Establish a connection to the database
    connection = sqlite3.connect(db_file)

    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Execute SQL commands to create tables and initialize data
    with open('schema.sql', 'r') as schema_file:
        schema_script = schema_file.read()
        cursor.executescript(schema_script)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()