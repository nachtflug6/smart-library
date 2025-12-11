from typing import Optional, Dict, Any, List
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _from_json

from smart_library.domain.entities.embedding import Embedding
import sqlite3
import pickle
from datetime import datetime
from smart_library.infrastructure.repositories.entity_repository import EntityRepository



import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional

class VectorRepository(BaseRepository):
    table = "vector"  # sqlite-vec virtual table

    @staticmethod
    def normalize(vec):
        v = np.array(vec, dtype=float)
        return (v / np.linalg.norm(v)).tolist()

    def add_vector(self, id: str, vector: List[float], model: str, created_by=None):
        """
        Store ONE embedding row per vector, as required by sqlite-vec.
        Vector is normalized so cosine similarity works.
        """
        # ensure entity exists
        entity_repo = EntityRepository()
        if not entity_repo.exists(id):
            now = datetime.utcnow().isoformat()
            entity_repo.create(
                id=id,
                entity_kind="Vector",
                created_by=created_by,
                metadata={}
            )

        vec_norm = self.normalize(vector)

        sql = """
        INSERT INTO vector(rowid, embedding, model)
        VALUES (?, ?, ?)
        """
        self.conn.execute(sql, (id, str(vec_norm), model))
        self.conn.commit()
        return id

    def get_vector(self, id: str):
        row = self.conn.execute("""
            SELECT rowid, embedding, model
            FROM vector
            WHERE rowid = ?
        """, (id,)).fetchone()

        if not row:
            return None

        return {
            "id": row["rowid"],
            "vector": eval(row["embedding"]),
            "model": row["model"],
        }

    def search_similar_vectors(self, query_vector: List[float], top_k=10, model: Optional[str] = None):
        """
        Cosine similarity search using sqlite-vec MATCH operator.
        """
        query = str(self.normalize(query_vector))

        if model:
            sql = """
            SELECT rowid, distance, model
            FROM vector
            WHERE model = ? AND embedding MATCH ?
            ORDER BY distance
            LIMIT ?
            """
            params = (model, query, top_k)
        else:
            sql = """
            SELECT rowid, distance, model
            FROM vector
            WHERE embedding MATCH ?
            ORDER BY distance
            LIMIT ?
            """
            params = (query, top_k)

        rows = self.conn.execute(sql, params).fetchall()

        results = []
        for row in rows:
            dist = row["distance"]
            cosine = 1 - (dist * dist) / 2
            results.append({
                "id": row["rowid"],
                "cosine_similarity": cosine,
                "distance": dist,
                "model": row["model"]
            })

        return results