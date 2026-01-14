from typing import List, Optional
from smart_library.application.models.search_response import SearchSession, SearchResponse, SearchResult


class RankingService:
    """Service to compute a reranked query vector (Rocchio) and fetch similar vectors."""

    def __init__(self):
        pass

    def rerank_from_session(
        self,
        session: SearchSession,
        embedding_service,
        text_service,
        vector_service,
        top_k: int = 20,
        alpha: float = 1.0,
        beta: float = 0.75,
        gamma: float = 0.15,
    ) -> SearchResponse:
        """Takes a SearchSession (with query and positive/negative IDs) and returns
        a SearchResponse with ranked results using Rocchio reranking.
        
        Args:
            session: SearchSession containing query, positive_ids, and negative_ids.
                     positive_ids and negative_ids can be empty for initial searches.
            embedding_service: service providing `embed(text)`.
            text_service: service providing `get_text(text_id)`.
            vector_service: service providing `search_similar_vectors(vec, top_k)`.
            top_k: number of results to return.
            alpha/beta/gamma: Rocchio weights (alpha for query, beta for positives, gamma for negatives).
            
        Returns:
            SearchResponse with results populated and ranked by similarity.
        """
        import numpy as np

        # Embed the query
        q_vec = None
        try:
            q_vec = embedding_service.embed(session.query)
        except Exception:
            q_vec = None

        if q_vec is None:
            raise RuntimeError("Failed to embed query for rerank")

        pos_vecs: List[List[float]] = []
        neg_vecs: List[List[float]] = []

        # Embed positive texts
        for vid in session.positive_ids:
            try:
                txt = text_service.get_text(vid)
                if not txt:
                    continue
                emb_source = getattr(txt, "embedding_content", None) or getattr(txt, "display_content", None) or getattr(txt, "content", None)
                if not emb_source:
                    continue
                vec = embedding_service.embed(emb_source)
                if vec:
                    pos_vecs.append(vec)
            except Exception:
                continue

        # Embed negative texts
        for vid in session.negative_ids:
            try:
                txt = text_service.get_text(vid)
                if not txt:
                    continue
                emb_source = getattr(txt, "embedding_content", None) or getattr(txt, "display_content", None) or getattr(txt, "content", None)
                if not emb_source:
                    continue
                vec = embedding_service.embed(emb_source)
                if vec:
                    neg_vecs.append(vec)
            except Exception:
                continue

        # Compute Rocchio-adjusted query vector
        q = np.array(q_vec, dtype=float)
        new_q = alpha * q

        if pos_vecs:
            pos_arr = np.array(pos_vecs, dtype=float)
            if pos_arr.size:
                pos_mean = np.mean(pos_arr, axis=0)
                new_q = new_q + beta * pos_mean

        if neg_vecs:
            neg_arr = np.array(neg_vecs, dtype=float)
            if neg_arr.size:
                neg_mean = np.mean(neg_arr, axis=0)
                new_q = new_q - gamma * neg_mean

        # Search for similar vectors using the adjusted query
        results = vector_service.search_similar_vectors(new_q.tolist(), top_k=top_k)

        # Build SearchResponse with results
        response = SearchResponse(query=session.query)
        for i, r in enumerate(results, start=1):
            rid = r.get("id")
            score = r.get("cosine_similarity") or r.get("score") or 0.0
            is_pos = rid in session.positive_ids
            is_neg = rid in session.negative_ids
            response.results.append(SearchResult(rank=i, id=rid, score=score, is_positive=is_pos, is_negative=is_neg))

        return response
