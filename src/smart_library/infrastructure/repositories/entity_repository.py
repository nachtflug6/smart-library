from typing import Optional, Dict, Any
from smart_library.infrastructure.repositories.base_repository import BaseRepository
from smart_library.domain.entities.entity import Entity

class EntityRepository(BaseRepository[Entity]):
    table = "entity"
    columns = {
        "id": "id",
        "created_at": "created_at",
        "modified_at": "modified_at",
        "created_by": "created_by",
        "updated_by": "updated_by",
        "parent_id": "parent_id",
        "entity_kind": "entity_kind",
        "metadata": "metadata",
    }
    json_columns = {"metadata"}

    def __init__(self):
        super().__init__()

    def get(self, entity_id: str) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM entity WHERE id=?"
        row = self.conn.execute(sql, (entity_id,)).fetchone()
        return dict(row) if row else None

    def exists(self, entity_id: str) -> bool:
        return self.get(entity_id) is not None

    def list(self, type: str = None, limit: int = 50):
        """
        List entities, optionally filtered by entity_kind, with a limit.
        """
        if type:
            sql = "SELECT * FROM entity WHERE entity_kind = ? LIMIT ?"
            rows = self.conn.execute(sql, (type, limit)).fetchall()
        else:
            sql = "SELECT * FROM entity LIMIT ?"
            rows = self.conn.execute(sql, (limit,)).fetchall()
        return [dict(row) for row in rows]