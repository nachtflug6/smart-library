from typing import Optional, Dict, Any, List
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _from_json
from smart_library.domain.entities.embedding import Embedding
import sqlite3
import pickle

class EmbeddingRepository(BaseRepository):
    """
    Repository for the 'embedding' table.
    """

    table = "embedding"

    def add(self, embedding: Embedding):
        # Insert into entity table first (handles id, parent_id, etc.)
        self._insert_entity(embedding)
        sql = """
        INSERT INTO embedding (id, vector, model, dim)
        VALUES (?, ?, ?, ?)
        """
        # Store the vector as a BLOB using pickle
        vector_blob = sqlite3.Binary(pickle.dumps(embedding.vector))
        self.conn.execute(sql, [
            embedding.id,
            vector_blob,
            embedding.model,
            len(embedding.vector)
        ])
        self.conn.commit()
        return embedding.id

    def get(self, embedding_id: str) -> Optional[Embedding]:
        sql = "SELECT * FROM embedding WHERE id = ?"
        row = self.conn.execute(sql, [embedding_id]).fetchone()
        if not row:
            return None
        # Unpickle the vector
        vector = pickle.loads(row["vector"])
        return Embedding(
            id=row["id"],
            vector=vector,
            parent_id="",  # parent_id is in the entity table
            model=row["model"],
            metadata={},   # metadata is not stored in embedding table
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    def delete(self, embedding_id: str):
        sql = "DELETE FROM embedding WHERE id = ?"
        self.conn.execute(sql, [embedding_id])
        self.conn.commit()

    def list(self) -> List[Embedding]:
        sql = f"SELECT * FROM {self.table}"
        rows = self.conn.execute(sql).fetchall()
        return [self.get(row["id"]) for row in rows]

    def get_for_parent(self, parent_id: str) -> Optional[Embedding]:
        """
        Get the embedding for a given parent entity (by parent_id in the entity table).
        """
        sql = """
        SELECT embedding.*, entity.parent_id
        FROM embedding
        JOIN entity ON embedding.id = entity.id
        WHERE entity.parent_id = ?
        """
        row = self.conn.execute(sql, [parent_id]).fetchone()
        if not row:
            return None
        vector = pickle.loads(row["vector"])
        return Embedding(
            id=row["id"],
            vector=vector,
            parent_id=row["parent_id"],
            model=row["model"],
            metadata={},
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    @classmethod
    def default_instance(cls):
        from smart_library.infrastructure.db.db import get_connection
        conn = get_connection()
        return cls(conn)