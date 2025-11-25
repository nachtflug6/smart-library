from typing import Optional, Dict, Any
import json

from smart_library.domain.entities.term import Term
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _to_json, _from_json

class TermRepository(BaseRepository[Term]):
    table = "term"
    columns = {
        "id": "id",
        "canonical_name": "canonical_name",
        "sense": "sense",
        "aliases": "aliases",              # JSON
        "domain": "domain",
        "definition": "definition",
        "related_terms": "related_terms",  # JSON
    }
    json_columns = {"aliases", "related_terms"}

    def row_to_entity(self, row: Dict[str, Any]) -> Term:
        data = dict(row)
        meta = json.loads(data["metadata"]) if data.get("metadata") else {}
        aliases = json.loads(data["aliases"]) if data.get("aliases") else []
        related = json.loads(data["related_terms"]) if data.get("related_terms") else []
        return Term(
            id=data.get("id"),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at"),
            parent_id=data.get("parent_id"),
            metadata=meta,
            canonical_name=data.get("canonical_name"),
            sense=data.get("sense"),
            definition=data.get("definition"),
            aliases=aliases,
            domain=data.get("domain"),
            related_terms=related,
        )

    def get_entity(self, entity_id: str) -> Optional[Term]:
        row = super().get(entity_id)
        if not row:
            return None
        return self.row_to_entity(row)

    def add(self, term: Term):
        self._insert_entity(term)
        sql = """
        INSERT INTO term (id, canonical_name, sense, definition, aliases, domain, related_terms)
        VALUES (?,?,?,?,?,?,?)
        """
        self.conn.execute(
            sql,
            [
                term.id,
                term.canonical_name,
                term.sense,
                term.definition,
                _to_json(term.aliases),
                term.domain,
                _to_json(term.related_terms),
            ],
        )
        self.conn.commit()
        return term.id

    def get(self, term_id: str) -> Optional[Term]:
        es = self._fetch_entity_row(term_id)
        if not es:
            return None
        row = self.conn.execute("SELECT * FROM term WHERE id=?", (term_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        return Term(
            id=es["id"],
            created_at=es["created_at"],
            modified_at=es["modified_at"],
            created_by=es.get("created_by"),
            updated_by=es.get("updated_by"),
            parent_id=es.get("parent_id"),
            metadata=_from_json(es.get("metadata"), {}),
            canonical_name=r["canonical_name"],
            sense=r.get("sense"),
            definition=r.get("definition"),
            aliases=_from_json(r.get("aliases"), []),
            domain=r.get("domain"),
            related_terms=_from_json(r.get("related_terms"), []),
        )

    def update(self, term: Term):
        self._update_entity_meta(term)
        sql = """
        UPDATE term SET canonical_name=?, sense=?, definition=?, aliases=?, domain=?, related_terms=? WHERE id=?
        """
        self.conn.execute(
            sql,
            [
                term.canonical_name,
                term.sense,
                term.definition,
                _to_json(term.aliases),
                term.domain,
                _to_json(term.related_terms),
                term.id,
            ],
        )
        self.conn.commit()

    def delete(self, term_id: str):
        self._delete_entity(term_id)
        self.conn.commit()

    def list(self, limit: int = 50):
        sql = "SELECT * FROM term LIMIT ?"
        rows = self.conn.execute(sql, (limit,)).fetchall()
        return [self.get(row["id"]) for row in rows]