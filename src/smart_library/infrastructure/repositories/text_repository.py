from typing import Optional, Dict, Any
import json

from smart_library.domain.entities.text import Text
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _from_json

class TextRepository(BaseRepository[Text]):
    table = "text_entity"

    def add(self, txt: Text):
        # Parent is page if available; else document
        if not txt.parent_id:
            txt.parent_id = txt.page_id or txt.document_id
        if not txt.parent_id:
            raise ValueError("Text.parent_id should reference Page or Document id")
        self._insert_entity(txt)
        sql = "INSERT INTO text_entity (id, type, chunk_index, content) VALUES (?,?,?,?)"
        self.conn.execute(sql, [txt.id, txt.type, txt.index, txt.content])
        self.conn.commit()
        return txt.id

    def get(self, text_id: str) -> Optional[Text]:
        es = self._fetch_entity_row(text_id)
        if not es:
            return None
        row = self.conn.execute("SELECT * FROM text_entity WHERE id=?", (text_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        return Text(
            id=es["id"],
            created_at=es["created_at"],
            modified_at=es["modified_at"],
            created_by=es.get("created_by"),
            updated_by=es.get("updated_by"),
            parent_id=es.get("parent_id"),
            metadata=_from_json(es.get("metadata"), {}),
            content=r["content"],
            text_type=r.get("type"),  # <-- FIXED: use text_type instead of type
            index=r.get("chunk_index"),
        )

    def update(self, txt: Text):
        self._update_entity_meta(txt)
        sql = "UPDATE text_entity SET type=?, chunk_index=?, content=? WHERE id=?"
        self.conn.execute(sql, [txt.type, txt.index, txt.content, txt.id])
        self.conn.commit()

    def delete(self, text_id: str):
        self._delete_entity(text_id)
        self.conn.commit()

    def list(self, doc_id: str = None, page_id: str = None, limit: int = 100):
        """
        List text chunks, optionally filtered by document or page, with a limit.
        """
        if page_id:
            sql = """
                SELECT text_entity.id FROM text_entity
                JOIN entity ON text_entity.id = entity.id
                WHERE entity.parent_id = ?
                LIMIT ?
            """
            rows = self.conn.execute(sql, (page_id, limit)).fetchall()
        elif doc_id:
            # Find all pages for the document, then all texts for those pages
            page_sql = "SELECT page.id FROM page JOIN entity ON page.id = entity.id WHERE entity.parent_id = ?"
            page_rows = self.conn.execute(page_sql, (doc_id,)).fetchall()
            page_ids = [row["id"] for row in page_rows]
            if not page_ids:
                return []
            placeholders = ",".join("?" for _ in page_ids)
            sql = f"""
                SELECT text_entity.id FROM text_entity
                JOIN entity ON text_entity.id = entity.id
                WHERE entity.parent_id IN ({placeholders})
                LIMIT ?
            """
            rows = self.conn.execute(sql, (*page_ids, limit)).fetchall()
        else:
            sql = "SELECT id FROM text_entity LIMIT ?"
            rows = self.conn.execute(sql, (limit,)).fetchall()
        return [self.get(row["id"]) for row in rows]