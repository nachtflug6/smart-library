from typer import Argument, echo
from smart_library.application.services.search_service import SearchService
from smart_library.application.models.search_response import SearchResponse, SearchResult
from smart_library.application.services.text_app_service import TextAppService
from smart_library.application.services.document_app_service import DocumentAppService
from smart_library.application.services.entity_app_service import EntityAppService
from smart_library.cli.main import app
import json
from pathlib import Path
from datetime import datetime
from typing import List

SESSION_FILE = Path.cwd() / ".search_session.json"


def _save_session(data: dict):
    try:
        SESSION_FILE.write_text(json.dumps(data, default=str), encoding="utf-8")
    except Exception as e:
        echo(f"Failed to save search session: {e}")


def _load_session() -> dict:
    try:
        if not SESSION_FILE.exists():
            return {}
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


@app.command(name="search")
def search(
    query: str = Argument(..., help="Text to search for"),
    top_k: int = Argument(20, help="Maximum number of results to show"),
):
    """
    Run a similarity search for `query` and show matching text ids and scores.
    """
    svc = SearchService()
    try:
        results = svc.similarity_search(query, top_k=top_k)
    except Exception as e:
        echo(f"Search failed: {e}")
        return []

    if not results:
        echo("No results found.")
        return []

    # Persist a searchable session mapping numeric result indexes to ids
    # Build a SearchResponse object and cache it to the session file
    session_obj = SearchResponse(query=query)
    # Cache query embedding
    try:
        qvec = svc.embedding_service.embed(query)
        session_obj.query_vector = qvec
    except Exception:
        session_obj.query_vector = None
    for i, r in enumerate(results, start=1):
        rid = r.get("id")
        score = r.get("cosine_similarity") or r.get("cosine") or r.get("score") or 0.0
        # set flags if labels were already present for this id
        lbl = session_obj.labels.get(rid)
        is_pos = (lbl and lbl.get("label") == "pos")
        is_neg = (lbl and lbl.get("label") == "neg")
        session_obj.results.append(SearchResult(rank=i, id=rid, score=score, is_positive=is_pos, is_negative=is_neg))
        # try to fetch stored vector; if not available, defer embedding until rerank but attempt here
        try:
            vec = svc.vector_service.get_vector(rid)
            if vec and "vector" in vec:
                session_obj.cached_embeddings[rid] = vec["vector"]
        except Exception:
            # ignore: fallback to re-embedding later
            pass
    _save_session(session_obj.to_dict())

    # Use the boxed visualization if available; fall back to compact lines
    try:
        from smart_library.utils.print import print_search_response
        text_svc = TextAppService()
        doc_svc = DocumentAppService()
        entity_svc = EntityAppService()
        # use the structured SearchResponse printer
        print_search_response(session_obj, text_svc, doc_service=doc_svc, entity_service=entity_svc)
    except Exception:
        # fallback: print minimal numbered results
        for res in session_obj.results:
            echo(f"{res.rank}: {res.id} | score={res.score:.4f}")
    return results


@app.command(name="label")
def label(
    identifier: str = Argument(..., help="Result rank (number) or entity id to label"),
    lbl: str = Argument(..., help="Label: pos or neg"),
):
    """Label a previous search result by numeric rank or by entity id as positive (`pos`) or negative (`neg`)."""
    session_raw = _load_session()
    if not session_raw or "results" not in session_raw:
        echo("No search session found. Run `smartlib search <query>` first.")
        return
    session = SearchResponse.from_dict(session_raw)
    if lbl not in ("pos", "neg"):
        echo("Label must be 'pos' or 'neg'.")
        return
    # Determine id from identifier: if numeric -> rank, else assume id
    rid = None
    try:
        rank = int(identifier)
        matches = [r for r in session.get("results", []) if r.get("rank") == rank]
        if not matches:
            echo(f"No result with rank {rank} in last session.")
            return
        rid = matches[0].get("id")
    except Exception:
        # treat identifier as id
        rid = identifier
        # ensure this id appeared in last results (optional)
        if not any(r.get("id") == rid for r in session.get("results", [])):
            echo(f"Warning: id {rid} was not in last search results; still storing label.")

    session.labels[rid] = {"id": rid, "label": lbl}
    # update result flags if present
    for res in session.results:
        if res.id == rid:
            res.is_positive = (lbl == "pos")
            res.is_negative = (lbl == "neg")
    _save_session(session.to_dict())
    echo(f"Labeled {rid} as {lbl}.")


@app.command(name="rerank")
def rerank(alpha: float = Argument(1.0, help="Alpha weight for original query"),
           beta: float = Argument(0.75, help="Beta weight for positives"),
           gamma: float = Argument(0.15, help="Gamma weight for negatives"),
           top_k: int = Argument(20, help="Number of reranked results to return")):
    """Apply Rocchio reranking to the last search using labeled positives/negatives."""
    session_raw = _load_session()
    if not session_raw or "results" not in session_raw:
        echo("No search session found. Run `smartlib search <query>` first.")
        return []

    session = SearchResponse.from_dict(session_raw)
    labels = session.labels
    if not labels:
        echo("No labels found in session. Use `smartlib label <rank> pos|neg` to add labels.")
        return []

    svc = SearchService()
    # embed original query
    try:
        q_vec = svc.embedding_service.embed(session.query)
    except Exception as e:
        echo(f"Failed to embed query: {e}")
        return []

    # Collect positive and negative vectors using cached embeddings if available,
    # otherwise re-embed text contents and cache them in session.
    pos_vecs: List[List[float]] = []
    neg_vecs: List[List[float]] = []
    text_svc = TextAppService()
    for vid, info in labels.items():
        labelv = info.get("label")
        # vid is entity id (labels keyed by id)
        txt = text_svc.get_text(vid)
        if not txt:
            echo(f"Warning: no text found for id {vid}")
            continue
        # Prefer explicit embedding_content, then display_content, then content
        emb_source = getattr(txt, "embedding_content", None) or getattr(txt, "display_content", None) or getattr(txt, "content", None)
        if not emb_source:
            echo(f"Warning: text {vid} has no content to embed")
            continue
        # Try cached session embedding first
        cached = session.cached_embeddings.get(vid)
        if cached:
            vec = cached
        else:
            try:
                vec = svc.embedding_service.embed(emb_source)
                # cache persistently in session
                session.cached_embeddings[vid] = vec
                _save_session(session.to_dict())
            except Exception as e:
                echo(f"Failed to embed text {vid}: {e}")
                continue
        if labelv == "pos":
            pos_vecs.append(vec)
        else:
            neg_vecs.append(vec)

    import numpy as np
    q = np.array(q_vec, dtype=float)
    new_q = alpha * q
    if pos_vecs:
        pos_mean = np.mean(np.array(pos_vecs, dtype=float), axis=0)
        new_q = new_q + beta * pos_mean
    if neg_vecs:
        neg_mean = np.mean(np.array(neg_vecs, dtype=float), axis=0)
        new_q = new_q - gamma * neg_mean

    # Use vector service to search with new query vector
    vsvc = svc.vector_service
    try:
        results = vsvc.search_similar_vectors(new_q.tolist(), top_k=top_k)
    except Exception as e:
        echo(f"Rerank search failed: {e}")
        return []

    # Persist rerank results in session
    session.rerank_results = [{"rank": i+1, "id": r.get("id"), "score": r.get("cosine_similarity")} for i, r in enumerate(results)]
    _save_session(session.to_dict())

    # Print reranked numbered results
    echo("Reranked results:")
    for i, r in enumerate(results, start=1):
        score = r.get("cosine_similarity") or r.get("score") or 0.0
        echo(f"{i}: {r.get('id')} | score={score:.4f}")
    return results