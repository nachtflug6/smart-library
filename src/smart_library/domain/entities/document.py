from dataclasses import dataclass, field
from typing import Dict, Optional, List

from smart_library.domain.entities.entity import Entity

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Document(Entity):

    # -----------------------------
    # Identity / Classification
    # -----------------------------
    type: Optional[str] = None  # "research_article", "book", "thesis", "pdf", "webpage", etc.

    # -----------------------------
    # Provenance & Source Tracking
    # -----------------------------
    source_path: Optional[str] = None   # local file
    source_url: Optional[str] = None    # remote URL
    source_format: Optional[str] = None # pdf, html, txt
    file_hash: Optional[str] = None     # deduplication

    version: Optional[str] = None       # v1, v2, etc.

    # -----------------------------
    # Structure
    # -----------------------------
    page_count: Optional[int] = None

    # -----------------------------
    # Bibliographic Metadata
    # -----------------------------
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    doi: Optional[str] = None
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    venue: Optional[str] = None
    year: Optional[int] = None

    # -----------------------------
    # Citation metadata (optional)
    # -----------------------------
    reference_list: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)