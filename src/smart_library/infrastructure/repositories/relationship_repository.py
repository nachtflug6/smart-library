from typing import Optional, Dict, Any
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _to_json, _from_json

class RelationshipRepository(BaseRepository):
    """
    Repository for the 'relationship' table.
    """

    table = "relationship"

    def add(self, relationship_id: str, source_id: str, target_id: str, type: str, metadata: Optional[Dict[str, Any]] = None):
        sql = f"""
        INSERT INTO {self.table} (id, source_id, target_id, type, metadata)
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
        sql = f"SELECT * FROM {self.table} WHERE id = ?"
        row = self.conn.execute(sql, [relationship_id]).fetchone()
        if not row:
            return None
        data = dict(row)
        data["metadata"] = _from_json(data["metadata"], {})
        return data

    def delete(self, relationship_id: str):
        sql = f"DELETE FROM {self.table} WHERE id = ?"
        self.conn.execute(sql, [relationship_id])
        self.conn.commit()

    def list(self, type: str = None, limit: int = 50):
        """
        List relationships, optionally filtered by type, with a limit.
        """
        if type:
            sql = f"SELECT * FROM {self.table} WHERE type = ? LIMIT ?"
            rows = self.conn.execute(sql, (type, limit)).fetchall()
        else:
            sql = f"SELECT * FROM {self.table} LIMIT ?"
            rows = self.conn.execute(sql, (limit,)).fetchall()
        return [dict(row) for row in rows]