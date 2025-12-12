"""
Integration context: provides make_context() to wire up real services and DB for integration tests.
"""
from smart_library.domain.services.vector_service import VectorService
# Import other services as needed

class IntegrationContext:
    def __init__(self, db_path=None):
        # Optionally allow disposable DBs for test isolation
        self.db_path = db_path or ':memory:'
        # Wire up services (optionally pass db_path to repo/services)
        self.vector_service = VectorService()
        # Add more services as needed


def make_context(db_path=None):
    """Create a new integration context with all real services wired up."""
    return IntegrationContext(db_path=db_path)
