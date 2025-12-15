from dataclasses import dataclass, field
from typing import Optional, List
from smart_library.domain.entities.entity import Entity

@dataclass
class Heading(Entity):
    title: str = None
    index: Optional[int] = None
    page_number: int = 0
