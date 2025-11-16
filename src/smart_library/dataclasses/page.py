from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Page:
    page_number: int
    page_text: str

    def __post_init__(self) -> None:
        if not isinstance(self.page_number, int) or self.page_number < 1:
            raise ValueError("page_number must be an integer >= 1")
        if not isinstance(self.page_text, str):
            raise TypeError("page_text must be a string")

    # Compatibility shim if other code expects `page.text`
    @property
    def text(self) -> str:
        return self.page_text