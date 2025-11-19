# File: /workspaces/smart-library/src/smart_library/infrastructure/db/import_entities.py

import sqlite3
from contextlib import closing

def get_connection(db_file=':memory:'):
    """Establish a database connection to the SQLite database specified by db_file.
    
    Args:
        db_file (str): The database file path. Defaults to an in-memory database.
    
    Returns:
        sqlite3.Connection: Connection object to the SQLite database.
    """
    conn = sqlite3.connect(db_file)
    return conn

def import_entity(entity_data):
    """Import an entity into the database.
    
    Args:
        entity_data (dict): A dictionary containing entity data to be imported.
    """
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        # Assuming entity_data contains a table name and values to insert
        table_name = entity_data.get('table')
        values = entity_data.get('values')
        
        placeholders = ', '.join('?' * len(values))
        sql = f'INSERT INTO {table_name} VALUES ({placeholders})'
        
        cursor.execute(sql, tuple(values))
        conn.commit()

def import_entities(entities):
    """Import multiple entities into the database.
    
    Args:
        entities (list): A list of dictionaries containing entity data to be imported.
    """
    for entity in entities:
        import_entity(entity)