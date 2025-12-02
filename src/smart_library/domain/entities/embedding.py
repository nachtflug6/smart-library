from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .entity import Entity

@dataclass
class Embedding(Entity):
    vector: List[float] = field(default_factory=list)
    model: Optional[str] = None