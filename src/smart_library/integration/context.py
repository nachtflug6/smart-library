"""
Integration context: provides make_context() to wire up real services and DB for integration tests.
"""
import tempfile
import os
from smart_library.application.services.vector_service import VectorService
# Import other services as needed


class IntegrationContext:
    def __init__(self, db_path=None):
        # If no db_path is provided, create a temporary file for the DB
        self._temp_db_file = None
        if db_path is None:
            tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
            self.db_path = tmp.name
            tmp.close()
            self._temp_db_file = self.db_path
        else:
            self.db_path = db_path

        # Initialize schema for the new DB
        from pathlib import Path
        from smart_library.infrastructure.db.db import migrate_schema
        schema_path = Path(__file__).parent.parent / "infrastructure" / "db" / "schema.sql"
        migrate_schema(schema_path=schema_path)

        # Wire up services (optionally pass db_path to repo/services)
        # If your VectorService or its repo can take a db_path, pass it here
        self.vector_service = VectorService()
        # Add more services as needed

    def cleanup(self):
        # Remove the temp DB file if it was created
        if self._temp_db_file and os.path.exists(self._temp_db_file):
            os.remove(self._temp_db_file)


def make_context(db_path=None):
    """Create a new integration context with all real services wired up."""
    return IntegrationContext(db_path=db_path)
