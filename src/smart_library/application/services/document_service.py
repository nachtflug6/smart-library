# smart_library/application/services/document_service.py

from typing import Optional, List
from smart_library.domain.entities.document import Document
from smart_library.application.services.base_service import BaseService
from smart_library.infrastructure.repositories.document_repository import DocumentRepository
from smart_library.infrastructure.repositories.page_repository import PageRepository


class DocumentService(BaseService):
    def __init__(self, document_repo):
        super().__init__(document_repo)
        self.document_repo = document_repo

    @classmethod
    def default_instance(cls):
        repo = DocumentRepository()
        return cls(repo)

    # -------------------------------
    # CREATE
    # -------------------------------
    def add_document(self, doc: Document) -> str:
        self.touch(doc)
        return self.document_repo.add(doc)

    # -------------------------------
    # READ
    # -------------------------------
    def get_document(self, doc_id: str) -> Optional[Document]:
        return self.document_repo.get(doc_id)

    def list_documents(self) -> List[Document]:
        return self.document_repo.list_all()

    def find_by_doi(self, doi: str) -> Optional[Document]:
        return self.document_repo.find_by_doi(doi)

    def get_pages(self, doc_id: str):
        """
        Return all pages for the given document ID.
        """
        page_repo = PageRepository()
        return page_repo.list(doc_id=doc_id)

    # -------------------------------
    # UPDATE
    # -------------------------------
    def update_document(self, doc: Document):
        self.touch(doc)
        return self.document_repo.update(doc)

    def update_document_metadata(self, doc_id: str, metadata: dict):
        doc = self.get_document(doc_id)
        if doc is None:
            raise ValueError(f"Document not found: {doc_id}")
        self.update_metadata(doc, metadata)
        self.touch(doc)
        return self.document_repo.update(doc)

    # -------------------------------
    # DELETE
    # -------------------------------
    def delete_document(self, doc_id: str):
        return self.document_repo.delete(doc_id)
