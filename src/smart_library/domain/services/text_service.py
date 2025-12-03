# smart_library/application/services/text_service.py

from typing import Optional, List
from smart_library.domain.entities.text import Text
from smart_library.domain.services.base_service import BaseService
from smart_library.infrastructure.repositories.text_repository import TextRepository
from smart_library.infrastructure.repositories.entity_repository import EntityRepository


class TextService(BaseService):
    """
    Service for handling Text entities (chunks, summaries, captions, titles).
    """

    def __init__(self, text_repo, entity_repo, embedding_service=None):
        """
        text_repo: TextRepository
        entity_repo: for validating the parent exists (Document or Page)
        embedding_service: optional embedding generator
        """
        super().__init__(text_repo)
        self.text_repo = text_repo
        self.entity_repo = entity_repo
        self.embedding_service = embedding_service

    @classmethod
    def default_instance(cls):
        text_repo = TextRepository()
        entity_repo = EntityRepository()
        return cls(text_repo, entity_repo)

    # -------------------------------
    # CREATE
    # -------------------------------
    def add_text(self, text: Text) -> str:
        # parent must exist
        if text.parent_id is None:
            raise ValueError("Text.parent_id must reference a Document or Page")

        parent = self.entity_repo.get(text.parent_id)
        if parent is None:
            raise ValueError(f"Parent entity does not exist: {text.parent_id}")

        # timestamp
        self.touch(text)

        # optional: embed automatically
        if self.embedding_service:
            embedding = self.embedding_service.embed(text.content)
            text.metadata["embedding"] = embedding

        return self.text_repo.add(text)

    # -------------------------------
    # READ
    # -------------------------------
    def get_text(self, text_id: str) -> Optional[Text]:
        return self.text_repo.get(text_id)

    def list_for_parent(self, parent_id: str) -> List[Text]:
        return self.text_repo.list_for_parent(parent_id)

    def list_by_type(self, parent_id: str, text_type: str) -> List[Text]:
        return self.text_repo.list_by_type(parent_id, text_type)

    def get_all_for_document(self, doc_id: str) -> List[Text]:
        """
        Return all Texts (chunks) that belong to all pages of a document.
        """
        # Assuming you have a PageRepository or can access pages for a document
        from smart_library.infrastructure.repositories.page_repository import PageRepository
        page_repo = PageRepository()
        pages = page_repo.list(doc_id=doc_id)
        all_texts = []
        for page in pages:
            texts = self.text_repo.list_for_parent(page.id)
            all_texts.extend(texts)
        return all_texts

    def get_all_for_page(self, page_id: str) -> List[Text]:
        """
        Return all Texts (chunks) for a given page.
        """
        return self.text_repo.list_for_parent(page_id)

    # -------------------------------
    # UPDATE
    # -------------------------------
    def update_text(self, text: Text):
        self.touch(text)

        # embedding updated when content changes
        if self.embedding_service:
            text.metadata["embedding"] = self.embedding_service.embed(text.content)

        return self.text_repo.update(text)

    def update_text_metadata(self, text_id: str, metadata: dict):
        text = self.text_repo.get(text_id)
        if text is None:
            raise ValueError(f"Text entity not found: {text_id}")

        self.update_metadata(text, metadata)
        self.touch(text)

        return self.text_repo.update(text)

    # -------------------------------
    # DELETE
    # -------------------------------
    def delete_text(self, text_id: str):
        return self.text_repo.delete(text_id)
