"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import List, Optional, Set


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(10, description="Number of results to return", ge=1, le=100)


class SearchResult(BaseModel):
    """Individual search result schema."""
    rank: int
    id: str
    score: float
    is_positive: bool = False
    is_negative: bool = False


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    results: List[SearchResult]
    total: int


class RerankRequest(BaseModel):
    """Rerank request schema."""
    query: str = Field(..., description="Search query text")
    positive_ids: List[str] = Field(default=[], description="List of positive example text IDs")
    negative_ids: List[str] = Field(default=[], description="List of negative example text IDs")
    top_k: int = Field(10, description="Number of results to return", ge=1, le=100)


class LabelRequest(BaseModel):
    """Label request schema."""
    result_id: str = Field(..., description="ID of the text result to label")
    label: str = Field(..., description="Label type: 'pos' or 'neg'")


class LabelResponse(BaseModel):
    """Label response schema."""
    success: bool
    message: str


class DocumentAddRequest(BaseModel):
    """Document add request schema."""
    path: str = Field(..., description="Path to PDF file")
    debug: bool = Field(False, description="Enable debug output")


class DocumentAddResponse(BaseModel):
    """Document add response schema."""
    success: bool
    document_id: Optional[str] = None
    message: str


class DocumentListResponse(BaseModel):
    """Document list response schema."""
    documents: List[dict]
    total: int


class DocumentDetailResponse(BaseModel):
    """Document detail response schema."""
    id: str
    title: Optional[str]
    authors: Optional[List[str]]
    year: Optional[int]
    abstract: Optional[str]
    doi: Optional[str]
    page_count: Optional[int]
    source_path: Optional[str]


class TextContentResponse(BaseModel):
    """Text content response schema."""
    id: str
    content: str
    display_content: Optional[str] = None
    text_type: Optional[str] = None
    page_number: Optional[int] = None
    character_count: Optional[int] = None
    parent_id: Optional[str] = None
    metadata: Optional[dict] = None
