from smart_library.infrastructure.repositories.entity_repository import EntityRepository
from smart_library.domain.services.base_service import BaseService

class EntityService(BaseService):
    """
    Service for entity creation, retrieval, and management.
    Wraps EntityRepository and provides business logic for entities.
    """
    def __init__(self, repo=None):
        super().__init__(repo or EntityRepository())

    def create_entity(self, id, entity_kind, created_by=None, metadata=None, parent_id=None):
        """
        Create a new entity record.
        """
        # Optionally, add business logic here (e.g., check parent existence)
        return self.repo.create(id, entity_kind, created_by, metadata, parent_id)

    def get_entity(self, entity_id):
        return self.repo.get(entity_id)

    def entity_exists(self, entity_id):
        return self.repo.exists(entity_id)

    def list_entities(self, type=None, limit=50):
        return self.repo.list(type=type, limit=limit)
