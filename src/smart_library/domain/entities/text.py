from dataclasses import dataclass
from typing import Optional

from smart_library.domain.entities.entity import Entity
from smart_library.domain.constants.text_types import TextType

@dataclass
class Text(Entity):
    title: str = ""
    content: str = ""
    # Rename to avoid clashing with Entity.type property; maps to DB column "type"
    text_type: str = TextType.CHUNK      # "chunk", "summary", "caption", etc.
    index: Optional[int] = None          # for ordering inside a page or document
    character_count: Optional[int] = None
    token_count: Optional[int] = None

    # Relations to satisfy schema.text_entity
    document_id: Optional[str] = None
    page_id: Optional[str] = None
