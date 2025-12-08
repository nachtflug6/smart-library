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
    affiliations: List[Affiliation] = field(default_factory=list)  # <-- add this

@dataclass
class Header:
    title: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    doi: Optional[str] = None
    md5: Optional[str] = None
    authors: List[Author] = field(default_factory=list)
    affiliations: Dict[str, Affiliation] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    abstract: Optional[str] = None
