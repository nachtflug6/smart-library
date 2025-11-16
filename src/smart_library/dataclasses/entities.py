from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from .document import Document
from .page import Page

EntityType = Literal["document", "page", "text", "term"]


@dataclass(slots=True)
class Entity:
    """Single entity entry with id, type, and data."""
    id: str
    type: EntityType
    data: Dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("id must be a non-empty string")
        if self.type not in ("document", "page", "text", "term"):
            raise ValueError(f"type must be one of: document, page, text, term (got {self.type})")
        if not isinstance(self.data, dict):
            raise TypeError("data must be a dictionary")


@dataclass(slots=True)
class Entities:
    """Collection of entities with typed access methods."""
    entities: List[Entity] = field(default_factory=list)
    _index: Dict[str, Entity] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        # Build internal index by id
        self._index = {e.id: e for e in self.entities}
        # Annotate page entities with parent document_id if missing
        for e in self.entities:
            self._annotate_page_document_id(e)

    def _infer_document_id(self, page_entity_id: str) -> Optional[str]:
        # Expect format: <document_id>_p<digits>, e.g., "doc-001_p0001"
        m = re.match(r"^(?P<doc>.+)_p(?P<num>\d+)$", page_entity_id)
        if not m:
            return None
        return m.group("doc")

    def _annotate_page_document_id(self, entity: Entity) -> None:
        if entity.type != "page":
            return
        if "document_id" not in entity.data or not isinstance(entity.data.get("document_id"), str):
            doc_id = self._infer_document_id(entity.id)
            if doc_id:
                entity.data["document_id"] = doc_id

    def add(self, entity: Entity) -> None:
        """Add an entity to the collection."""
        if entity.id in self._index:
            raise ValueError(f"Entity with id '{entity.id}' already exists")
        # Ensure page entities carry document_id
        self._annotate_page_document_id(entity)
        self.entities.append(entity)
        self._index[entity.id] = entity

    def get(self, entity_id: str) -> Optional[Entity]:
        """Get entity by id."""
        return self._index.get(entity_id)

    def get_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities if e.type == entity_type]

    def get_document(self, entity_id: str) -> Optional[Document]:
        """Get a Document entity by id and convert to Document object.
        
        Pages are loaded by reference: page_id = {document_id}_p{page_number:04d}
        """
        entity = self.get(entity_id)
        if entity is None or entity.type != "document":
            return None
        
        # Get page_count from document data
        page_count = entity.data.get("page_count", 0)
        if not isinstance(page_count, int) or page_count < 0:
            return Document(pages=[])
        
        # Load pages by constructing page_ids
        pages = []
        for page_num in range(1, page_count + 1):
            page_id = f"{entity_id}_p{page_num:04d}"
            page = self.get_page(page_id)
            if page is not None:
                pages.append(page)
        
        return Document(pages=pages)

    def get_page(self, entity_id: str) -> Optional[Page]:
        """Get a Page entity by id and convert to Page object."""
        entity = self.get(entity_id)
        if entity is None or entity.type != "page":
            return None
        
        # Reconstruct Page from data
        return Page(
            page_number=entity.data["page_number"],
            page_text=entity.data["page_text"]
        )

    def get_text(self, entity_id: str) -> Optional[str]:
        """Get text content from a text entity."""
        entity = self.get(entity_id)
        if entity is None or entity.type != "text":
            return None
        return entity.data.get("content")

    def get_term(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get term data from a term entity."""
        entity = self.get(entity_id)
        if entity is None or entity.type != "term":
            return None
        return entity.data

    @classmethod
    def load(cls, path: Union[str, Path]) -> "Entities":
        """Load entities from JSONL file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        entities = []
        with path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    entity = Entity(
                        id=obj["id"],
                        type=obj["type"],
                        data=obj.get("data", {})
                    )
                    entities.append(entity)
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    raise ValueError(f"Invalid entity at line {line_num}: {e}") from e
        
        return cls(entities=entities)

    def write(self, path: Union[str, Path]) -> None:
        """Write entities to JSONL file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with path.open("w", encoding="utf-8") as f:
            for entity in self.entities:
                obj = {
                    "id": entity.id,
                    "type": entity.type,
                    "data": entity.data
                }
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    def __len__(self) -> int:
        return len(self.entities)

    def __contains__(self, entity_id: str) -> bool:
        return entity_id in self._index