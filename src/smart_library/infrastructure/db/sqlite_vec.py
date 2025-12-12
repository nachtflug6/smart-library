import sqlite3
try:
    from sqlite_vec import loadable_path
except ImportError:
    import os
    def loadable_path():
        return os.getenv("SQLITE_VEC_PATH", "/home/vscode/.local/lib/python3.11/site-packages/sqlite_vec/vec0.so")

def load_sqlitevec_extension(conn: sqlite3.Connection):
    """Load the sqlite-vec extension into a SQLite connection."""
    conn.enable_load_extension(True)
    conn.load_extension(loadable_path())
    conn.enable_load_extension(False)