from dataclasses import dataclass, field
from typing import Dict, Optional, List

from smart_library.domain.entities.entity import Entity

@dataclass
class Term(Entity):
    # Surface form (the literal string)
    canonical_name: str                  # e.g., "Kalman"

    # Disambiguation category (sense)
    sense: Optional[str] = None          # e.g., "person", "algorithm", "theorem", "company"

    definition: Optional[str] = None

    # Aliases / Variants / Synonyms
    aliases: List[str] = field(default_factory=list)

    # Domain (optional)
    domain: Optional[str] = None         # e.g., "CS", "control", "stats"

    # Relations to other terms
    related_terms: List[str] = field(default_factory=list)