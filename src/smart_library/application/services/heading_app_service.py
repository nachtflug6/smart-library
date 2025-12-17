from typing import Optional, List

from smart_library.infrastructure.repositories.heading_repository import HeadingRepository
from smart_library.domain.entities.heading import Heading


class HeadingAppService:
    def __init__(self, repo: Optional[HeadingRepository] = None):
        self.repo = repo or HeadingRepository()

    def add_heading(self, heading: Heading) -> str:
        return self.repo.add(heading)

    def get_heading(self, heading_id: str) -> Optional[Heading]:
        return self.repo.get(heading_id)

    def list_for_parent(self, parent_id: str) -> List[Heading]:
        return self.repo.list_for_parent(parent_id)

    def close(self):
        try:
            self.repo.conn.close()
        except Exception:
            pass
