from dataclasses import dataclass, field
from typing import Optional, List
from smart_library.domain.entities.entity import Entity
from smart_library.domain.constants.relationship_types import RelationshipType

@dataclass
class Relationship(Entity):

    source_id: str = None
    target_id: str = None
    type: RelationshipType = RelationshipType.BELONGS_TO

