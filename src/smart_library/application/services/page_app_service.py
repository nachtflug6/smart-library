from typing import Optional

from smart_library.infrastructure.repositories.page_repository import PageRepository
from smart_library.domain.entities.page import Page


class PageAppService:
    def __init__(self, repo: Optional[PageRepository] = None):
        self.repo = repo or PageRepository()

    def add_page(self, page: Page) -> str:
        return self.repo.add(page)

    def get_page(self, page_id: str) -> Optional[Page]:
        return self.repo.get(page_id)

    def update_page(self, page: Page) -> None:
        return self.repo.update(page)
