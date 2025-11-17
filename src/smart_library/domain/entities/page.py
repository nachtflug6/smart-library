from dataclasses import dataclass, field
from typing import Dict, Optional, List

from smart_library.domain.entities.entity import Entity

@dataclass
class Page(Entity):
    page_number: int

    # Optional extracted content
    full_text: Optional[str] = None
    token_count: Optional[int] = None

    # Optional structural hints (lightweight)
    paragraphs: List[str] = field(default_factory=list)
    sections: List[str] = field(default_factory=list)

    # Optional classification
    is_reference_page: Optional[bool] = None
    is_title_page: Optional[bool] = None

    # Optional visual markers
    has_tables: Optional[bool] = None
    has_figures: Optional[bool] = None
    has_equations: Optional[bool] = None
