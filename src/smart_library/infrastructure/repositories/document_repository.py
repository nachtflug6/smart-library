from typing import Optional, Dict, Any
import json

from smart_library.domain.entities.document import Document
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _to_json, _from_json


class DocumentRepository(BaseRepository[Document]):
    table = "document"
    # Map DB columns to Document attributes
    columns = {
        "id": "id",
        "type": "doc_type",          # classification, not Entity.type
        "source_path": "source_path",
        "source_uri": "source_url",  # dataclass uses source_url
        "source_format": "source_format",
        "file_hash": "file_hash",
        "version": "version",
        "title": "title",
        "authors": "authors",        # JSON
        "keywords": "keywords",      # JSON
        "doi": "doi",
        "publication_date": "publication_date",
        "publisher": "publisher",
        "venue": "venue",
        "year": "year",
        "page_count": "page_count",
    }
    json_columns = {"authors", "keywords"}

    def row_to_entity(self, row: Dict[str, Any]) -> Document:
        # Split e.* and c.* fields after join; prefer child alias keys
        # Normalize JSON fields
        data = dict(row)
        # SQLite Row may prefix duplicate column names; handle both
        authors = data.get("authors")
        keywords = data.get("keywords")
        if isinstance(authors, str) and authors:
            try:
                authors = json.loads(authors)
            except Exception:
                authors = None
        if isinstance(keywords, str) and keywords:
            try:
                keywords = json.loads(keywords)
            except Exception:
                keywords = None

        # Map DB -> dataclass args
        return Document(
            id=data.get("id"),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at"),
            parent_id=data.get("parent_id"),
            # metadata comes as TEXT JSON from entity table
            # Safe-load metadata if present
            **({
                "metadata": json.loads(data["metadata"])
            } if data.get("metadata") else {}),
            type=data.get("type"),
            source_path=data.get("source_path"),
            source_url=data.get("source_uri"),
            source_format=data.get("source_format"),
            file_hash=data.get("file_hash"),
            version=data.get("version"),
            title=data.get("title"),
            authors=authors,
            keywords=keywords,
            doi=data.get("doi"),
            publication_date=data.get("publication_date"),
            publisher=data.get("publisher"),
            venue=data.get("venue"),
            year=data.get("year"),
            page_count=data.get("page_count"),
        )

    def get_entity(self, entity_id: str) -> Optional[Document]:
        row = super().get(entity_id)
        if not row:
            return None
        return self.row_to_entity(row)

    def add(self, doc: Document):
        self._insert_entity(doc)
        sql = """
        INSERT INTO document (id, type, source_path, source_url, source_format, file_hash,
                              version, page_count, title, authors, keywords, doi,
                              publication_date, publisher, venue, year, reference_list, citations)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        self.conn.execute(
            sql,
            [
                doc.id,
                doc.type,
                doc.source_path,
                doc.source_url,
                doc.source_format,
                doc.file_hash,
                doc.version,
                doc.page_count,
                doc.title,
                _to_json(doc.authors),
                _to_json(doc.keywords),
                doc.doi,
                doc.publication_date,
                doc.publisher,
                doc.venue,
                doc.year,
                _to_json(doc.reference_list),
                _to_json(doc.citations),
            ],
        )
        self.conn.commit()
        return doc.id

    def get(self, doc_id: str) -> Optional[Document]:
        es = self._fetch_entity_row(doc_id)
        if not es:
            return None
        row = self.conn.execute("SELECT * FROM document WHERE id=?", (doc_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        return Document(
            id=es["id"],
            created_at=es["created_at"],
            modified_at=es["modified_at"],
            created_by=es.get("created_by"),
            updated_by=es.get("updated_by"),
            parent_id=es.get("parent_id"),
            metadata=_from_json(es.get("metadata"), {}),
            type=r.get("type"),
            source_path=r.get("source_path"),
            source_url=r.get("source_url"),
            source_format=r.get("source_format"),
            file_hash=r.get("file_hash"),
            version=r.get("version"),
            page_count=r.get("page_count"),
            title=r.get("title"),
            authors=_from_json(r.get("authors"), None),
            keywords=_from_json(r.get("keywords"), None),
            doi=r.get("doi"),
            publication_date=r.get("publication_date"),
            publisher=r.get("publisher"),
            venue=r.get("venue"),
            year=r.get("year"),
            reference_list=_from_json(r.get("reference_list"), []),
            citations=_from_json(r.get("citations"), []),
        )

    def update(self, doc: Document):
        self._update_entity_meta(doc)
        sql = """
        UPDATE document SET
            type=?, source_path=?, source_url=?, source_format=?, file_hash=?,
            version=?, page_count=?, title=?, authors=?, keywords=?, doi=?,
            publication_date=?, publisher=?, venue=?, year=?, reference_list=?, citations=?
        WHERE id=?
        """
        self.conn.execute(
            sql,
            [
                doc.type,
                doc.source_path,
                doc.source_url,
                doc.source_format,
                doc.file_hash,
                doc.version,
                doc.page_count,
                doc.title,
                _to_json(doc.authors),
                _to_json(doc.keywords),
                doc.doi,
                doc.publication_date,
                doc.publisher,
                doc.venue,
                doc.year,
                _to_json(doc.reference_list),
                _to_json(doc.citations),
                doc.id,
            ],
        )
        self.conn.commit()

    def delete(self, doc_id: str):
        self._delete_entity(doc_id)
        self.conn.commit()

    def list(self, limit: int = 50):
        """
        List documents, limited to `limit` results.
        """
        sql = "SELECT * FROM document LIMIT ?"
        rows = self.conn.execute(sql, (limit,)).fetchall()
        return [self.row_to_entity(row) for row in rows]
