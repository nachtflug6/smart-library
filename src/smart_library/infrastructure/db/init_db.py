import os
import sqlite3
from pathlib import Path

DB_PATH = "db/smart_library.db"
SCHEMA_PATH = "src/smart_library/db/schema.sql"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():

    if os.path.exists(DB_PATH):
        print("[DB] Database already exists — skipping init.")
        return
    
    print("[DB] Initializing new database...")
    conn = get_connection()

    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()

    print("[ok] schema applied:", DB_PATH)

if __name__ == "__main__":
    init_db()
