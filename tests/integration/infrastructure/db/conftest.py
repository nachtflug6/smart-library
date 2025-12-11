import os
import pytest
from smart_library.infrastructure.db.db import migrate_schema, get_connection_with_sqlitevec
from smart_library.config import DB_PATH

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Override config for tests
    os.environ["SMARTLIB_DATA_DIR"] = "/workspace/tests/integration/data"
    # Remove old test DB if exists
    if DB_PATH.exists():
        DB_PATH.unlink()
    # Migrate schema to create fresh test DB
    migrate_schema()
    # Ensure sqlite-vec extension is loaded for the test DB
    conn = get_connection_with_sqlitevec(load_sqlitevec=True)
    conn.close()
    yield
    # Cleanup after tests
    if DB_PATH.exists():
        DB_PATH.unlink()