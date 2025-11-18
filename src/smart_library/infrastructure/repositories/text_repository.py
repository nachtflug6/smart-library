from typing import Optional, Dict, Any
import json

from smart_library.domain.entities.text import Text
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _from_json

class TextRepository(BaseRepository[Text]):
    def add(self, txt: Text):
        # Parent is page if available; else document
        if not txt.parent_id:
            txt.parent_id = txt.page_id or txt.document_id
        else:
            raise ValueError("Text.parent_id should reference Page or Document id")
        self._insert_entity(txt)
        sql = "INSERT INTO text_entity (id, type, index, content) VALUES (?,?,?,?)"
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
            type=r.get("type"),
            index=r.get("index"),
        )

    def update(self, txt: Text):
        self._update_entity_meta(txt)
        sql = "UPDATE text_entity SET type=?, index=?, content=? WHERE id=?"
        self.conn.execute(sql, [txt.type, txt.index, txt.content, txt.id])
        self.conn.commit()

    def delete(self, text_id: str):
        self._delete_entity(text_id)
        self.conn.commit()