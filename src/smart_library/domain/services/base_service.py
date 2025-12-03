from datetime import datetime

from smart_library.domain.entities.entity import Entity

class BaseService:
    def __init__(self, repo):
        self.repo = repo

    def touch(self, entity, updated_by="system"):
        entity.modified_at = datetime.utcnow()
        entity.updated_by = updated_by
        return entity

    def update_metadata(self, entity, metadata: dict):
        entity.metadata.update(metadata)
        return entity

    def assert_parent_exists(self, repo, parent_id: str):
        if parent_id is None:
            raise ValueError("parent_id must be provided")
        if repo.get(parent_id) is None:
            raise ValueError(f"Parent entity '{parent_id}' does not exist: {parent_id}")
