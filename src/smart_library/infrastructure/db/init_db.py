import os
from smart_library.infrastructure.db import get_connection
from pathlib import Path

def init_db():
    schema_path = Path(__file__).parent / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    conn = get_connection()
    for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
        conn.execute(stmt)
    conn.commit()

if __name__ == "__main__":
    init_db()
