from dataclasses import dataclass, field
from typing import Dict, Optional, List

from smart_library.domain.entities.entity import Entity

@dataclass
class Term(Entity):
    canonical_name: str = ""
    sense: Optional[str] = None
    definition: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    domain: Optional[str] = None
    related_terms: List[str] = field(default_factory=list)