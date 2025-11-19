def get_connection():
    import sqlite3  # or the appropriate database library
    connection = sqlite3.connect('your_database.db')  # Update with your database path
    return connection

def import_metadata(metadata):
    connection = get_connection()
    cursor = connection.cursor()
    
    # Assuming metadata is a list of tuples for insertion
    for item in metadata:
        cursor.execute("INSERT INTO metadata_table (column1, column2) VALUES (?, ?)", item)
    
    connection.commit()
    cursor.close()
    connection.close()