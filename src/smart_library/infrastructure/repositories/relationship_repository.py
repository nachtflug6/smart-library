from typing import Optional, Dict, Any
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _to_json, _from_json

class RelationshipRepository(BaseRepository):
    """
    Repository for the 'relationship' table.
    """

    def add(self, relationship_id: str, source_id: str, target_id: str, type: str, metadata: Optional[Dict[str, Any]] = None):
        sql = """
        INSERT INTO relationship (id, source_id, target_id, type, metadata)
        VALUES (?, ?, ?, ?, ?)
        """
        self.conn.execute(sql, [
            relationship_id,
            source_id,
            target_id,
            type,
            _to_json(metadata or {})
        ])
        self.conn.commit()
        return relationship_id

    def get(self, relationship_id: str) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM relationship WHERE id = ?"
        row = self.conn.execute(sql, [relationship_id]).fetchone()
        if not row:
            return None
        data = dict(row)
        data["metadata"] = _from_json(data["metadata"], {})
        return data

    def delete(self, relationship_id: str):
        sql = "DELETE FROM relationship WHERE id = ?"
        self.conn.execute(sql, [relationship_id])
        self.conn.commit()