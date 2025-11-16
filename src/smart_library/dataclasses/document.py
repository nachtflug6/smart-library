from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from .page import Page


@dataclass(slots=True)
class Document:
    pages: List[Page] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Ensure sorted by page_number
        self.pages.sort(key=lambda p: p.page_number)

    @property
    def is_empty(self) -> bool:
        return len(self.pages) == 0

    @property
    def text(self) -> str:
        # Full text convenience (joins page_text)
        return "\n\n".join(p.page_text for p in self.pages)

    def add_page(self, page: Page) -> None:
        self.pages.append(page)
        self.pages.sort(key=lambda p: p.page_number)

    @classmethod
    def from_texts(cls, texts: Iterable[str], start_page: int = 1) -> "Document":
        pages = [Page(page_number=i, page_text=t) for i, t in enumerate(texts, start=start_page)]
        return cls(pages=pages)