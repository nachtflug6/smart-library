from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime

from smart_library.domain.entities.entity import Entity
from smart_library.domain.constants.text_types import TextType

@dataclass
class Text(Entity):
    content: str
    type: str = TextType.CHUNK      # "chunk", "summary", "caption", "title", etc.
    index: Optional[int] = None   # for ordering inside a page or document
