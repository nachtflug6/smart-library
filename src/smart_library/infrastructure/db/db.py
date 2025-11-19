import sqlite3
import os
from pathlib import Path

from smart_library.config import DB_PATH

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Get a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def migrate_schema(schema_path: Path = None):
    """Apply schema.sql to the database."""
    if schema_path is None:
        schema_path = Path(__file__).parent / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    conn = get_connection()
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()

def check_tables(expected_tables=None, db_path: Path = DB_PATH):
    """Check that expected tables exist in the database."""
    # These match the CREATE TABLE statements in schema.sql
    if expected_tables is None:
        expected_tables = {
            "entity",
            "document",
            "page",
            "text_entity",
            "term"
        }
    if not os.path.exists(db_path):
        return f"Database file not found: {db_path}"
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        tables = {row["name"] for row in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()}
        missing = expected_tables - tables
        if missing:
            return f"Missing tables: {', '.join(sorted(missing))}"
        return f"All expected tables present: {', '.join(sorted(expected_tables))}"
    finally:
        conn.close()

def init_db():
    """Initialize the database using the schema file."""
    migrate_schema()