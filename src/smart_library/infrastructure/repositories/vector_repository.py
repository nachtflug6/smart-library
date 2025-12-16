from typing import Optional, Dict, Any, List
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _from_json

import sqlite3
import pickle
from datetime import datetime
from smart_library.infrastructure.repositories.entity_repository import EntityRepository



import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional


class VectorRepository(BaseRepository):
    table = "vector"  # sqlite-vec virtual table (rowid = vector id)

    @staticmethod
    def default_instance():
        from smart_library.infrastructure.db.db import get_connection
        conn = get_connection()
        return VectorRepository(conn)

    @staticmethod
    def normalize(vec):
        v = np.array(vec, dtype=float)
        return (v / np.linalg.norm(v)).tolist()

    def add_vector(self, id: str, vector: List[float], created_by=None):
        """
        Store one vector per row in the sqlite-vec virtual table. id is TEXT PRIMARY KEY.
        Vector is normalized so cosine similarity works.
        """
        # Ensure a base `entity` row exists for this vector id.
        # Use the `EntityRepository` directly (validation utilities are in `entity_validation`).
        entity_repo = EntityRepository()
        if not entity_repo.exists(id):
            entity_repo.create(id=id, entity_kind="Vector", created_by=created_by, metadata={}, parent_id=None)

        vec_norm = self.normalize(vector)

        sql = """
        INSERT INTO vector(id, embedding)
        VALUES (?, ?)
        """
        self.conn.execute(sql, (id, str(vec_norm)))
        self.conn.commit()
        return id

    def get_vector(self, id: str):
        row = self.conn.execute(
            "SELECT id, embedding FROM vector WHERE id = ?",
            (id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "vector": eval(row["embedding"]),
        }

    def search_similar_vectors(self, query_vector: List[float], top_k=10):
        """
        Cosine similarity search using sqlite-vec MATCH operator.
        """
        query = str(self.normalize(query_vector))
        sql = """
        SELECT id, distance
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
                "id": row["id"],
                "cosine_similarity": cosine,
                "distance": dist
            })
        return results