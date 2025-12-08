from dataclasses import dataclass, field
from typing import Optional, List
from smart_library.domain.entities.entity import Entity
from smart_library.domain.entities.text import Text

@dataclass
class Page(Entity):
    page_number: int = 0
    document_id: Optional[str] = None  # Needed to satisfy schema.page.document_id

    # Optional extracted content
    full_text: Optional[str] = None
    token_count: Optional[int] = None

    # Optional structural hints (not persisted in current schema)
    paragraphs: List[str] = field(default_factory=list)
    sections: List[str] = field(default_factory=list)

    # Optional classification
    is_reference_page: Optional[bool] = None
    is_title_page: Optional[bool] = None

    # Optional visual markers
    has_tables: Optional[bool] = None
    has_figures: Optional[bool] = None
    has_equations: Optional[bool] = None

    texts: List[Text] = field(default_factory=list)  # <-- Add this
