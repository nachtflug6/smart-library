#!/usr/bin/env python3
"""Remove the configured DB file and reinitialize schema (skipping sqlite-vec block).

Usage: PYTHONPATH=src python3 scripts/reset_db.py
"""
from pathlib import Path
from smart_library.config import DB_PATH

schema_path = Path('src/smart_library/infrastructure/db/schema.sql')

if Path(DB_PATH).exists():
    Path(DB_PATH).unlink()
    print('Removed DB:', DB_PATH)
else:
    print('DB not present, will create at:', DB_PATH)

from smart_library.infrastructure.db.db import get_connection_with_sqlitevec

# Create DB and run schema without loading sqlite-vec
conn = get_connection_with_sqlitevec(DB_PATH, load_sqlitevec=False)
try:
    sql = schema_path.read_text(encoding='utf-8')
    if "DROP TABLE IF EXISTS vector;" in sql:
        start_idx = sql.find("DROP TABLE IF EXISTS vector;")
        next_sep = sql.find("\n-- =========================================================", start_idx)
        if next_sep != -1:
            sql = sql[:start_idx] + sql[next_sep:]
    conn.executescript(sql)
    conn.commit()
    print('Schema applied to', DB_PATH)
finally:
    conn.close()
