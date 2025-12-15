from dataclasses import dataclass
from typing import List
from smart_library.domain.entities.document import Document
from smart_library.domain.entities.text import Text
from smart_library.domain.entities.heading import Heading
from smart_library.domain.entities.page import Page
from smart_library.domain.entities.term import Term
from smart_library.domain.entities.relationship import Relationship

@dataclass(frozen=True)
class DocumentSnapshot:
    """
    An in-memory, non-persistent aggregate representing
    the current interpreted state of a document.
    """
    document: Document
    texts: List[Text]
    headings: List[Heading]
    pages: List[Page]
    relationships: List[Relationship]
    terms: List[Term]
