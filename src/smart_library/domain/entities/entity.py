from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

@dataclass
class Entity:
    id: str = field(default_factory=lambda: str(uuid4()))

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)

    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    parent_id: Optional[str] = ""

    metadata: Dict = field(default_factory=dict)

    @property
    def type(self) -> str:
        return self.__class__.__name__
