from typing import Optional
from smart_library.domain.entities.page import Page
from smart_library.infrastructure.repositories.base_repository import BaseRepository, _to_json, _from_json


class PageRepository(BaseRepository[Page]):
    table = "page"

    def add(self, page: Page):
        if not page.parent_id:
            raise ValueError("Page.parent_id must reference a Document.id")
        self._insert_entity(page)
        sql = """
        INSERT INTO page (id, page_number, full_text, token_count,
                          paragraphs, sections,
                          is_reference_page, is_title_page,
                          has_tables, has_figures, has_equations)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """
        self.conn.execute(
            sql,
            [
                page.id,
                page.page_number,
                page.full_text,
                page.token_count,
                _to_json(page.paragraphs),
                _to_json(page.sections),
                1 if page.is_reference_page else 0 if page.is_reference_page is not None else None,
                1 if page.is_title_page else 0 if page.is_title_page is not None else None,
                1 if page.has_tables else 0 if page.has_tables is not None else None,
                1 if page.has_figures else 0 if page.has_figures is not None else None,
                1 if page.has_equations else 0 if page.has_equations is not None else None,
            ],
        )
        self.conn.commit()
        return page.id

    def get(self, page_id: str) -> Optional[Page]:
        es = self._fetch_entity_row(page_id)
        if not es:
            return None
        row = self.conn.execute("SELECT * FROM page WHERE id=?", (page_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        return Page(
            id=es["id"],
            created_at=es["created_at"],
            modified_at=es["modified_at"],
            created_by=es.get("created_by"),
            updated_by=es.get("updated_by"),
            parent_id=es.get("parent_id"),
            metadata=_from_json(es.get("metadata"), {}),
            page_number=r["page_number"],
            full_text=r.get("full_text"),
            token_count=r.get("token_count"),
            paragraphs=_from_json(r.get("paragraphs"), []),
            sections=_from_json(r.get("sections"), []),
            is_reference_page=True if r.get("is_reference_page") == 1 else False if r.get("is_reference_page") == 0 else None,
            is_title_page=True if r.get("is_title_page") == 1 else False if r.get("is_title_page") == 0 else None,
            has_tables=True if r.get("has_tables") == 1 else False if r.get("has_tables") == 0 else None,
            has_figures=True if r.get("has_figures") == 1 else False if r.get("has_figures") == 0 else None,
            has_equations=True if r.get("has_equations") == 1 else False if r.get("has_equations") == 0 else None,
        )

    def update(self, page: Page):
        self._update_entity_meta(page)
        sql = """
        UPDATE page SET
            page_number=?, full_text=?, token_count=?,
            paragraphs=?, sections=?,
            is_reference_page=?, is_title_page=?,
            has_tables=?, has_figures=?, has_equations=?
        WHERE id=?
        """
        self.conn.execute(
            sql,
            [
                page.page_number,
                page.full_text,
                page.token_count,
                _to_json(page.paragraphs),
                _to_json(page.sections),
                1 if page.is_reference_page else 0 if page.is_reference_page is not None else None,
                1 if page.is_title_page else 0 if page.is_title_page is not None else None,
                1 if page.has_tables else 0 if page.has_tables is not None else None,
                1 if page.has_figures else 0 if page.has_figures is not None else None,
                1 if page.has_equations else 0 if page.has_equations is not None else None,
                page.id,
            ],
        )
        self.conn.commit()

    def delete(self, page_id: str):
        self._delete_entity(page_id)
        self.conn.commit()