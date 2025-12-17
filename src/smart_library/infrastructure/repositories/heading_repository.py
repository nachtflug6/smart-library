from typing import Optional, Dict, Any

from smart_library.domain.entities.heading import Heading
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _from_json
from smart_library.infrastructure.repositories.entity_repository import EntityRepository
from datetime import datetime
import json


class HeadingRepository(BaseRepository[Heading]):
    table = "heading"

    def add(self, heading: Heading):
        # Ensure base entity exists
        entity_repo = EntityRepository()
        if not entity_repo.exists(heading.id):
            now = datetime.utcnow().isoformat()
            sql_entity = """
            INSERT INTO entity (id, created_at, modified_at, created_by, updated_by, parent_id, entity_kind, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.conn.execute(sql_entity, [
                heading.id,
                now,
                now,
                getattr(heading, "created_by", None),
                getattr(heading, "updated_by", None),
                getattr(heading, "parent_id", None),
                "Heading",
                json.dumps(getattr(heading, "metadata", {})) if getattr(heading, "metadata", None) else None,
            ])
        sql = "INSERT INTO heading (id, title, \"index\", page_number) VALUES (?,?,?,?)"
        self.conn.execute(sql, [heading.id, heading.title, heading.index, heading.page_number])
        self.conn.commit()
        return heading.id

    def get(self, heading_id: str) -> Optional[Heading]:
        es = self._fetch_entity_row(heading_id)
        if not es:
            return None
        row = self.conn.execute("SELECT * FROM heading WHERE id=?", (heading_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        return Heading(
            id=es["id"],
            created_at=es["created_at"],
            modified_at=es["modified_at"],
            created_by=es.get("created_by"),
            updated_by=es.get("updated_by"),
            parent_id=es.get("parent_id"),
            metadata=_from_json(es.get("metadata"), {}),
            title=r.get("title"),
            index=r.get("index"),
            page_number=r.get("page_number"),
        )

    def delete(self, heading_id: str):
        self._delete_entity(heading_id)
        self.conn.commit()

    def list_for_parent(self, parent_id: str):
        sql = "SELECT id FROM heading JOIN entity ON heading.id = entity.id WHERE entity.parent_id = ? ORDER BY \"index\""
        rows = self.conn.execute(sql, (parent_id,)).fetchall()
        return [self.get(r["id"]) for r in rows]
