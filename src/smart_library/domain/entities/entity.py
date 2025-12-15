from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4


@dataclass
class Entity:
    """
    Base class for all domain entities.

    Guarantees:
    - Stable identity
    - Optional containment via parent_id
    - Passive lifecycle metadata
    - Opaque metadata for annotations
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    # Passive lifecycle metadata (managed outside the domain)
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)

    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    # Optional containment relationship
    parent_id: Optional[str] = None

    # Opaque annotations (domain logic must not depend on this)
    metadata: Dict = field(default_factory=dict)

    @property
    def type(self) -> str:
        """Return the domain entity type name."""
        return self.__class__.__name__
