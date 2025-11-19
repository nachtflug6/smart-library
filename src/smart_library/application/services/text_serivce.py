# smart_library/application/services/text_service.py

from typing import Optional, List
from smart_library.domain.entities.text import Text
from smart_library.application.services.base_service import BaseService


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
