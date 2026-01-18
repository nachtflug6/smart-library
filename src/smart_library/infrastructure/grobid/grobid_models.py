from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class Affiliation:
    key: str
    department: Optional[str] = None
    institution: Optional[str] = None
    settlement: Optional[str] = None
    country: Optional[str] = None

@dataclass
class Author:
    first_name: Optional[str] = None
    middle_names: List[str] = field(default_factory=list)
    last_name: Optional[str] = None
    email: Optional[str] = None
    affiliation_keys: List[str] = field(default_factory=list)
    org_names: List[str] = field(default_factory=list)
    affiliations: List['Affiliation'] = field(default_factory=list)

@dataclass
class Header:
    title: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    imprint_date: Optional[str] = None
    submission_note: Optional[str] = None
    doi: Optional[str] = None
    md5: Optional[str] = None
    authors: List[Author] = field(default_factory=list)
    affiliations: Dict[str, Affiliation] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    abstract: Optional[str] = None

@dataclass
class Surface:
    page: int
    ulx: float
    uly: float
    lrx: float
    lry: float

@dataclass
class Facsimile:
    surfaces: List[Surface] = field(default_factory=list)

@dataclass
class DocumentBody:
    sections: list["Section"] = field(default_factory=list)

@dataclass
class Section:
    id: Optional[str] = None
    title: Optional[str] = None
    coords: Optional["Coordinates"] = None  # <-- updated
    paragraphs: list["Paragraph"] = field(default_factory=list)

@dataclass
class Paragraph:
    text: str
    coords: Optional["Coordinates"] = None  # <-- updated
    references: list["InlineRef"] = field(default_factory=list)

@dataclass
class InlineRef:
    ref_type: str
    target: Optional[str]
    text: Optional[str]
    coords: Optional["Coordinates"] = None  # <-- updated

@dataclass
class CoordinateBox:
    page: int
    x1: float
    y1: float
    x2: float
    y2: float

@dataclass
class Coordinates:
    boxes: list[CoordinateBox]

    @property
    def pages(self) -> list[int]:
        return sorted({box.page for box in self.boxes})