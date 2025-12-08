from dataclasses import dataclass, field
from typing import Optional, List, Dict
from smart_library.domain.entities.entity import Entity
from smart_library.domain.entities.page import Page
from smart_library.domain.entities.text import Text
from datetime import datetime

@dataclass
class Document(Entity):

    # -----------------------------
    # Identity / Classification
    # -----------------------------
    type: Optional[str] = field(
        default=None,
        metadata={
            "format": "string, e.g., 'research_article', 'book', 'thesis', 'pdf', 'webpage'",
            "group": "identity",
            "llm_type": "string"
        }
    )

    # -----------------------------
    # Provenance & Source Tracking
    # -----------------------------
    source_path: Optional[str] = field(
        default=None,
        metadata={"format": "string, file path", "group": "provenance", "llm_type": "string"}
    )
    source_url: Optional[str] = field(
        default=None,
        metadata={"format": "string, URL", "group": "provenance", "llm_type": "string"}
    )
    source_format: Optional[str] = field(
        default=None,
        metadata={"format": "string, e.g., 'pdf', 'html', 'txt'", "group": "provenance", "llm_type": "string"}
    )
    file_hash: Optional[str] = field(
        default=None,
        metadata={"format": "string, hash value", "group": "provenance", "llm_type": "string"}
    )
    version: Optional[str] = field(
        default=None,
        metadata={"format": "string, e.g., 'v1', 'v2'", "group": "provenance", "llm_type": "string"}
    )

    # -----------------------------
    # Structure
    # -----------------------------
    page_count: Optional[int] = field(
        default=None,
        metadata={"format": "integer, number of pages", "group": "structure", "llm_type": "integer"}
    )
    pages: List[Page] = field(default_factory=list)
    texts: List[Text] = field(default_factory=list)

    # -----------------------------
    # Bibliographic Metadata
    # -----------------------------
    title: Optional[str] = field(
        default=None,
        metadata={"format": "string, title of the document", "group": "bibliographic", "llm_type": "string"}
    )
    authors: Optional[List[str]] = field(
        default=None,
        metadata={"format": "list of strings, e.g., ['Jane Doe', 'John Smith']", "group": "bibliographic", "llm_type": "list of strings"}
    )
    keywords: Optional[List[str]] = field(
        default=None,
        metadata={"format": "list of strings, e.g., ['deep learning', 'AI']", "group": "bibliographic", "llm_type": "list of strings"}
    )
    doi: Optional[str] = field(
        default=None,
        metadata={"format": "string, DOI identifier", "group": "bibliographic", "llm_type": "string"}
    )
    publication_date: Optional[str] = field(
        default=None,
        metadata={"format": "string, ISO date format 'YYYY-MM-DD' or year only", "group": "bibliographic", "llm_type": "string"}
    )
    publisher: Optional[str] = field(
        default=None,
        metadata={"format": "string, publisher name", "group": "bibliographic", "llm_type": "string"}
    )
    venue: Optional[str] = field(
        default=None,
        metadata={"format": "string, conference or journal name", "group": "bibliographic", "llm_type": "string"}
    )
    year: Optional[int] = field(
        default=None,
        metadata={"format": "integer, publication year", "group": "bibliographic", "llm_type": "integer"}
    )
    abstract: Optional[str] = field(
        default=None,
        metadata={"format": "string, abstract text", "group": "bibliographic", "llm_type": "string"}
    )

    # -----------------------------
    # Citation metadata (optional)
    # -----------------------------
    reference_list: List[str] = field(
        default_factory=list,
        metadata={"format": "list of strings, reference entries", "group": "citation", "llm_type": "list of strings"}
    )
    citations: List[str] = field(
        default_factory=list,
        metadata={"format": "list of strings, citation entries", "group": "citation", "llm_type": "list of strings"}
    )

    def get_fields_by_group(self, group: str) -> List[str]:
        """
        Returns a list of field names belonging to the specified metadata group.
        """
        return [
            name for name, field_obj in self.__dataclass_fields__.items()
            if field_obj.metadata.get("group") == group
        ]

    def get_field_types_for_group(self, group: str) -> Dict[str, str]:
        """
        Returns a dict of field names and LLM type descriptions for the specified group.
        """
        return {
            name: field_obj.metadata.get("llm_type", "string")
            for name, field_obj in self.__dataclass_fields__.items()
            if field_obj.metadata.get("group") == group
        }
