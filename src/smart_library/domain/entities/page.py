from dataclasses import dataclass, field
from typing import Optional, List, Dict
from smart_library.domain.entities.entity import Entity


@dataclass
class Page(Entity):
    page_number: Optional[int] = None
    full_text: Optional[str] = None
    token_count: Optional[int] = None
    paragraphs: List[str] = field(default_factory=list)
    sections: List[Dict] = field(default_factory=list)

    is_reference_page: Optional[bool] = None
    is_title_page: Optional[bool] = None
    has_tables: Optional[bool] = None
    has_figures: Optional[bool] = None
    has_equations: Optional[bool] = None
