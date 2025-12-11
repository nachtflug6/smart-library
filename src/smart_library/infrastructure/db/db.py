import sqlite3
import os
from pathlib import Path



from smart_library.config import DB_PATH
from smart_library.infrastructure.db.sqlite_vec import load_sqlitevec_extension

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Get a SQLite connection with foreign keys enabled. Always load sqlite-vec extension."""
    return get_connection_with_sqlitevec(db_path, load_sqlitevec=True)

def get_connection_with_sqlitevec(db_path: Path = DB_PATH, load_sqlitevec: bool = False, sqlitevec_path: str = None) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    # Always load sqlite-vec extension unless explicitly disabled
    if load_sqlitevec or load_sqlitevec is None:
        try:
            load_sqlitevec_extension(conn)
        except Exception as e:
            raise RuntimeError(f"Failed to load sqlite-vec extension: {e}")
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

def check_tables(expected_tables=None, db_path: Path = DB_PATH, check_sqlitevec: bool = False):
    """Check that expected tables exist in the database. Optionally check sqlite-vec vector tables."""
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
    conn = get_connection_with_sqlitevec(db_path, load_sqlitevec=check_sqlitevec)
    try:
        cur = conn.cursor()
        tables = {row["name"] for row in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()}
        missing = expected_tables - tables
        result = []
        if missing:
            result.append(f"Missing tables: {', '.join(sorted(missing))}")
        else:
            result.append(f"All expected tables present: {', '.join(sorted(expected_tables))}")
        # Optionally check sqlite-vec vector tables
        if check_sqlitevec:
            vector_tables = [row["name"] for row in cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_vec';"
            ).fetchall()]
            if not vector_tables:
                result.append("WARNING: No sqlite-vec vector tables found.")
            else:
                result.append(f"Found sqlite-vec tables: {', '.join(vector_tables)}")
        return "\n".join(result)
    finally:
        conn.close()
def check_sqlitevec_index(db_path: Path = DB_PATH, table_name: str = "document_vec"):
    """Check sqlite-vec index health for a given vector table."""
    if not os.path.exists(db_path):
        return f"Database file not found: {db_path}"
    conn = get_connection_with_sqlitevec(db_path, load_sqlitevec=True)
    try:
        cur = conn.cursor()
        # Check if table exists
        tables = {row["name"] for row in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()}
        if table_name not in tables:
            return f"Vector table '{table_name}' not found."
        # Check row count
        count = cur.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        # Optionally, check for sqlite-vec index integrity
        try:
            info = cur.execute(f"SELECT * FROM {table_name} LIMIT 1").description
            columns = [col[0] for col in info]
        except Exception as e:
            columns = []
        return f"Table '{table_name}' row count: {count}, columns: {columns}"
    finally:
        conn.close()

def init_db():
    """Initialize the database using the schema file."""
    migrate_schema()