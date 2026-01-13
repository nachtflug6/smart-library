from dataclasses import dataclass, field
from typing import Optional, List
from smart_library.domain.constants.document_types import DocumentType
from smart_library.domain.entities.entity import Entity

@dataclass
class Document(Entity):

    # -----------------------------
    # Identity / Classification
    # -----------------------------
    type: Optional[DocumentType] = field(default=None)

    # -----------------------------
    # Provenance & Source Tracking
    # -----------------------------
    source_path: Optional[str] = field(default=None)
    source_url: Optional[str] = field(default=None)
    source_format: Optional[str] = field(default=None)
    file_hash: Optional[str] = field(default=None)
    version: Optional[str] = field(default=None)
    citation_key: Optional[str] = field(default=None)
    human_id: Optional[str] = field(default=None)

    # -----------------------------
    # Structure
    # -----------------------------
    page_count: Optional[int] = field(default=None)

    # -----------------------------
    # Bibliographic Metadata
    # -----------------------------
    title: Optional[str] = field(default=None)
    authors: Optional[List[str]] = field(default=None)
    doi: Optional[str] = field(default=None)
    publication_date: Optional[str] = field(default=None)
    publisher: Optional[str] = field(default=None)
    venue: Optional[str] = field(default=None)
    year: Optional[int] = field(default=None)
    abstract: Optional[str] = field(default=None)
