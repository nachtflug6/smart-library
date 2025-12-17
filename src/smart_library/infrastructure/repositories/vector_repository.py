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

        # Avoid inserting duplicate rows for the same id: remove existing entry first.
        try:
            self.conn.execute("DELETE FROM vector WHERE id=?", (id,))
            sql = """
            INSERT INTO vector(id, embedding)
            VALUES (?, ?)
            """
            self.conn.execute(sql, (id, str(vec_norm)))
            self.conn.commit()
            return id
        except Exception:
            # If the vec virtual table doesn't exist, fall back to a regular table.
            # Create fallback table if missing and insert there.
            try:
                self.conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vector_fallback (
                        id TEXT PRIMARY KEY,
                        embedding TEXT,
                        norm REAL,
                        created_by TEXT,
                        created_at TEXT
                    )
                    """
                )
                # remove existing fallback row
                try:
                    self.conn.execute("DELETE FROM vector_fallback WHERE id=?", (id,))
                except Exception:
                    pass
                now = datetime.utcnow().isoformat()
                self.conn.execute(
                    "INSERT INTO vector_fallback(id, embedding, norm, created_by, created_at) VALUES (?, ?, ?, ?, ?)",
                    (id, str(vec_norm), float(np.linalg.norm(vec_norm)), created_by, now)
                )
                self.conn.commit()
                return id
            except Exception:
                # Give up and bubble up the original failure
                raise

    def get_vector(self, id: str):
        # try primary vec table
        try:
            row = self.conn.execute(
                "SELECT id, embedding FROM vector WHERE id = ?",
                (id,)
            ).fetchone()
            if row:
                return {"id": row["id"], "vector": eval(row["embedding"])}
        except Exception:
            pass
        # try fallback table
        try:
            row = self.conn.execute(
                "SELECT id, embedding FROM vector_fallback WHERE id = ?",
                (id,)
            ).fetchone()
            if not row:
                return None
            return {"id": row["id"], "vector": eval(row["embedding"])}
        except Exception:
            return None

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
        # First attempt: sqlite-vec MATCH query
        try:
            rows = self.conn.execute(sql, params).fetchall()
            results = []
            seen = set()
            for row in rows:
                rid = row["id"]
                if rid in seen:
                    continue
                seen.add(rid)
                dist = row["distance"]
                cosine = 1 - (dist * dist) / 2
                results.append({"id": rid, "cosine_similarity": cosine, "distance": dist})
                if len(results) >= top_k:
                    break
            return results
        except Exception:
            # Fallback: use vector_fallback table and brute-force cosine similarity in Python
            try:
                rows = self.conn.execute("SELECT id, embedding FROM vector_fallback").fetchall()
            except Exception:
                return []
            q = np.array(self.normalize(query_vector), dtype=float)
            candidates = []
            for row in rows:
                try:
                    vid = row["id"]
                    v = np.array(eval(row["embedding"]), dtype=float)
                    # embeddings stored normalized already in add_vector; ensure norm
                    if np.linalg.norm(v) == 0:
                        continue
                    cosine = float(np.dot(q, v) / (np.linalg.norm(q) * np.linalg.norm(v)))
                    candidates.append((vid, cosine))
                except Exception:
                    continue
            candidates.sort(key=lambda x: x[1], reverse=True)
            results = []
            for vid, cosine in candidates[:top_k]:
                results.append({"id": vid, "cosine_similarity": float(cosine)})
            return results