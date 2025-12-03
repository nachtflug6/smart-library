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
    abstract: Optional[str] = None  # Added abstract field

    # -----------------------------
    # Citation metadata (optional)
    # -----------------------------
    reference_list: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)

    # Metadata group definitions (non-invasive)
    METADATA_GROUPS: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "identity": ["type"],
            "provenance": ["source_path", "source_url", "source_format", "file_hash", "version"],
            "structure": ["page_count"],
            "bibliographic": ["title", "authors", "keywords", "doi", "publication_date", "publisher", "venue", "year", "abstract"],
            "citation": ["reference_list", "citations"],
        },
        init=False,
        repr=False
    )
    
    def get_bibliographic_field_types(self) -> Dict[str, str]:
        """
        Returns a dictionary mapping bibliographic metadata field names to their type names as strings.
        """
        bib_fields = self.METADATA_GROUPS.get("bibliographic", [])
        field_types = {}
        for field_name in bib_fields:
            if field_name in self.__dataclass_fields__:
                type_str = str(self.__dataclass_fields__[field_name].type)
                type_str = (
                    type_str.replace("typing.", "")
                            .replace("NoneType", "None")
                            .replace("class '", "")
                            .replace("'", "")
                )
                field_types[field_name] = type_str
        return field_types
