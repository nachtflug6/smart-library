import sqlite3
from pathlib import Path

def init_db():
    db_path = "db/smart_library.db"
    schema_path = "src/smart_library/db/schema.sql"

    # Ensure folder exists
    Path("db").mkdir(exist_ok=True)

    with sqlite3.connect(db_path) as conn, open(schema_path, "r") as f:
        conn.executescript(f.read())

    print("[ok] schema applied:", db_path)


if __name__ == "__main__":
    init_db()
