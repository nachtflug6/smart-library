from dataclasses import dataclass
from typing import Optional

from smart_library.domain.entities.entity import Entity
from smart_library.domain.constants.text_types import TextType

@dataclass
class Text(Entity):
    content: str = "" # canonical extracted text
    display_content: str = "" # For display purposes
    embedding_content: str = "" # For embedding/model input

    text_type: TextType = TextType.CHUNK      # "chunk", "summary", "caption", etc.
    index: Optional[int] = None # for ordering inside a page or document
    character_count: Optional[int] = None
    token_count: Optional[int] = None
    page_number: Optional[int] = None
