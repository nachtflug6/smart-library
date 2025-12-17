from typing import Optional, Dict, Any

from smart_library.infrastructure.repositories.entity_repository import EntityRepository


class EntityAppService:
    """Application-level wrapper for `EntityRepository`.

    Keeps repository access out of domain code and provides a small
    convenience API used by higher-level services and scenarios.
    """

    def __init__(self, repo: Optional[EntityRepository] = None):
        self.repo = repo or EntityRepository()

    def exists(self, entity_id: str) -> bool:
        return self.repo.exists(entity_id)

    def get(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self.repo.get(entity_id)

    def create(self, id: str, entity_kind: str, created_by: str = None, metadata: dict = None, parent_id: str = None):
        return self.repo.create(id, entity_kind, created_by, metadata, parent_id)

    def ensure_exists(self, id: str, entity_kind: str, created_by: str = None, metadata: dict = None, parent_id: str = None) -> bool:
        """Ensure the entity exists in the DB; create it if missing.

        Returns True if a new entity was created, False if it already existed.
        """
        if not self.exists(id):
            self.create(id, entity_kind, created_by, metadata, parent_id)
            return True
        return False
