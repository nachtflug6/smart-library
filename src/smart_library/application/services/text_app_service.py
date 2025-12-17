from typing import Optional

from smart_library.infrastructure.repositories.text_repository import TextRepository
from smart_library.domain.entities.text import Text


class TextAppService:
    def __init__(self, repo: Optional[TextRepository] = None):
        self.repo = repo or TextRepository()

    def add_text(self, txt: Text) -> str:
        return self.repo.add(txt)

    def get_text(self, text_id: str) -> Optional[Text]:
        return self.repo.get(text_id)

    def update_text(self, txt: Text) -> None:
        return self.repo.update(txt)

    def exists(self, text_id: str) -> bool:
        return self.get_text(text_id) is not None

    def close(self):
        try:
            self.repo.conn.close()
        except Exception:
            pass
