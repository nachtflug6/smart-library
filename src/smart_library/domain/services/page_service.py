from typing import Optional

from smart_library.domain.entities.page import Page


class PageService:
    def __init__(self, page_repo=None, entity_repo=None):
        self.page_repo = page_repo
        self.entity_repo = entity_repo

    @classmethod
    def default_instance(cls):
        return cls()

    def add_page(self, page: Page):
        if not page.parent_id:
            raise ValueError("Page.parent_id must reference a Document.id")
        if self.entity_repo:
            parent = self.entity_repo.get(page.parent_id)
            if not parent:
                raise ValueError("Parent document not found: %s" % page.parent_id)
        return self.page_repo.add(page) if self.page_repo else None

    def get_page(self, page_id: str) -> Optional[Page]:
        if not self.page_repo:
            return None
        return self.page_repo.get(page_id)

    def update_page(self, page: Page):
        if not self.page_repo:
            return None
        return self.page_repo.update(page)

    def delete_page(self, page_id: str):
        if not self.page_repo:
            return None
        return self.page_repo.delete(page_id)
