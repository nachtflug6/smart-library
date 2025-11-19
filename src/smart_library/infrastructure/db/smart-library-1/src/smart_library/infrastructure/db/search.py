def get_connection():
    import sqlite3  # or the appropriate database connector
    connection = sqlite3.connect('your_database.db')  # Update with your database path
    return connection

def search_data(query):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def search_by_keyword(keyword):
    query = f"SELECT * FROM your_table WHERE your_column LIKE '%{keyword}%'"
    return search_data(query)

def search_by_id(record_id):
    query = f"SELECT * FROM your_table WHERE id = {record_id}"
    return search_data(query)