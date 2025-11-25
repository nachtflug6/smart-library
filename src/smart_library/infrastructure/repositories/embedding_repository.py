from typing import Optional, Dict, Any, List
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _to_json, _from_json

class EmbeddingRepository(BaseRepository):
    """
    Repository for the 'embedding' table.
    """

    table = "embedding"

    def add(self, embedding_id: str, vector: List[float], entity_id: str, model: str, metadata: Optional[Dict[str, Any]] = None):
        sql = """
        INSERT INTO embedding (id, vector, entity_id, model, metadata)
        VALUES (?, ?, ?, ?, ?)
        """
        self.conn.execute(sql, [
            embedding_id,
            _to_json(vector),
            entity_id,
            model,
            _to_json(metadata or {})
        ])
        self.conn.commit()
        return embedding_id

    def get(self, embedding_id: str) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM embedding WHERE id = ?"
        row = self.conn.execute(sql, [embedding_id]).fetchone()
        if not row:
            return None
        data = dict(row)
        data["vector"] = _from_json(data["vector"], [])
        data["metadata"] = _from_json(data["metadata"], {})
        return data

    def delete(self, embedding_id: str):
        sql = "DELETE FROM embedding WHERE id = ?"
        self.conn.execute(sql, [embedding_id])
        self.conn.commit()