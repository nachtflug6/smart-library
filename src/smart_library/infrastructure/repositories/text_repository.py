from typing import Optional, Dict, Any
import json


from smart_library.domain.entities.text import Text
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _from_json
from smart_library.infrastructure.repositories.entity_repository import EntityRepository
from datetime import datetime

class TextRepository(BaseRepository[Text]):
    table = "text_entity"

    def add(self, txt: Text):
        # Parent is page if available; else document
        if not txt.parent_id:
            txt.parent_id = txt.page_id or txt.document_id
        if not txt.parent_id:
            raise ValueError("Text.parent_id should reference Page or Document id")
        # Ensure entity exists
        entity_repo = EntityRepository()
        if not entity_repo.exists(txt.id):
            now = datetime.utcnow().isoformat()
            entity_kind = "Text"
            meta = txt.metadata if hasattr(txt, 'metadata') and txt.metadata is not None else {}
            sql_entity = """
            INSERT INTO entity (id, created_at, modified_at, created_by, updated_by, parent_id, entity_kind, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.conn.execute(sql_entity, [
                txt.id,
                now,
                now,
                getattr(txt, 'created_by', None),
                getattr(txt, 'updated_by', None),
                txt.parent_id,
                entity_kind,
                json.dumps(meta) if meta else None
            ])
        sql = (
            "INSERT INTO text_entity (id, type, text_type, chunk_index, \"index\", page_number, content, display_content, embedding_content, character_count, token_count)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)"
        )
        self.conn.execute(sql, [
            txt.id,
            txt.type,
            getattr(txt, "text_type", None),
            getattr(txt, "chunk_index", None) or getattr(txt, "index", None),
            getattr(txt, "index", None),
            getattr(txt, "page_number", None),
            getattr(txt, "content", None),
            getattr(txt, "display_content", None),
            getattr(txt, "embedding_content", None),
            getattr(txt, "character_count", None),
            getattr(txt, "token_count", None),
        ])
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
            content=r.get("content"),
            display_content=r.get("display_content"),
            embedding_content=r.get("embedding_content"),
            text_type=r.get("text_type") or r.get("type"),
            index=r.get("index") or r.get("chunk_index"),
            page_number=r.get("page_number"),
            character_count=r.get("character_count"),
            token_count=r.get("token_count"),
        )

    def update(self, txt: Text):
        self._update_entity_meta(txt)
        sql = "UPDATE text_entity SET type=?, text_type=?, chunk_index=?, \"index\"=?, page_number=?, content=?, display_content=?, embedding_content=?, character_count=?, token_count=? WHERE id=?"
        self.conn.execute(sql, [
            txt.type,
            getattr(txt, "text_type", None),
            getattr(txt, "chunk_index", None) or getattr(txt, "index", None),
            getattr(txt, "index", None),
            getattr(txt, "page_number", None),
            getattr(txt, "content", None),
            getattr(txt, "display_content", None),
            getattr(txt, "embedding_content", None),
            getattr(txt, "character_count", None),
            getattr(txt, "token_count", None),
            txt.id,
        ])
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