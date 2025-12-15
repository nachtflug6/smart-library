from dataclasses import dataclass, field
from typing import Dict, Optional, List

from smart_library.domain.entities.entity import Entity
from smart_library.domain.constants.term_types import TermType

@dataclass
class Term(Entity):
    canonical_name: str = ""
    type: TermType = TermType.EXTRACTED
    sense: Optional[str] = None
    definition: Optional[str] = None

