from typing import Optional

from smart_library.infrastructure.repositories.document_repository import DocumentRepository
from smart_library.domain.entities.document import Document


class DocumentAppService:
    def __init__(self, repo: Optional[DocumentRepository] = None):
        self.repo = repo or DocumentRepository()

    def add_document(self, doc: Document) -> str:
        return self.repo.add(doc)

    def update_document(self, doc: Document) -> None:
        return self.repo.update(doc)

    def get_document(self, doc_id: str) -> Optional[Document]:
        return self.repo.get(doc_id)
