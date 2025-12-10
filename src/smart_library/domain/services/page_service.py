from typing import Optional, List
from smart_library.domain.entities.page import Page
from smart_library.domain.services.base_service import BaseService
from smart_library.infrastructure.repositories.page_repository import PageRepository
from smart_library.infrastructure.repositories.entity_repository import EntityRepository

class PageService(BaseService):
    def __init__(self, page_repo, entity_repo=None):
        super().__init__(page_repo)
        self.page_repo = page_repo
        self.entity_repo = entity_repo

    @classmethod
    def default_instance(cls):
        page_repo = PageRepository()
        entity_repo = EntityRepository()
        return cls(page_repo, entity_repo)

    # CREATE
    def add_page(self, page: Page) -> str:
        if page.parent_id is None:
            raise ValueError("Page.parent_id must reference a Document")
        if self.entity_repo and self.entity_repo.get(page.parent_id) is None:
            raise ValueError(f"Parent entity does not exist: {page.parent_id}")
        self.touch(page)
        return self.page_repo.add(page)

    @staticmethod
    def create_page(**kwargs):
        # Add validation/normalization here if needed
        return Page(**kwargs)

    # READ
    def get_page(self, page_id: str) -> Optional[Page]:
        return self.page_repo.get(page_id)

    def list_pages_for_document(self, document_id: str) -> List[Page]:
        return self.page_repo.list_for_document(document_id)

    # UPDATE
    def update_page(self, page: Page):
        self.touch(page)
        return self.page_repo.update(page)

    def update_page_metadata(self, page_id: str, metadata: dict):
        page = self.get_page(page_id)
        if page is None:
            raise ValueError(f"Page not found: {page_id}")
        self.update_metadata(page, metadata)
        self.touch(page)
        return self.page_repo.update(page)

    # DELETE
    def delete_page(self, page_id: str):
        return self.page_repo.delete(page_id)