from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class SearchResult:
    rank: int
    id: str
    score: float
    is_positive: bool = False
    is_negative: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SearchResult":
        return SearchResult(
            rank=d.get("rank"),
            id=d.get("id"),
            score=d.get("score"),
            is_positive=d.get("is_positive", False),
            is_negative=d.get("is_negative", False),
        )


@dataclass
class SearchResponse:
    query: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    results: List[SearchResult] = field(default_factory=list)
    labels: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    cached_embeddings: Dict[str, List[float]] = field(default_factory=dict)
    query_vector: Optional[List[float]] = None
    rerank_results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "created_at": self.created_at,
            "results": [r.to_dict() for r in self.results],
            "labels": self.labels,
            "cached_embeddings": self.cached_embeddings,
            "query_vector": self.query_vector,
            "rerank_results": self.rerank_results,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SearchResponse":
        resp = SearchResponse(query=d.get("query", ""), created_at=d.get("created_at"))
        resp.results = [SearchResult.from_dict(r) for r in d.get("results", [])]
        resp.labels = d.get("labels", {}) or {}
        resp.cached_embeddings = d.get("cached_embeddings", {}) or {}
        resp.query_vector = d.get("query_vector")
        resp.rerank_results = d.get("rerank_results", []) or []
        return resp
