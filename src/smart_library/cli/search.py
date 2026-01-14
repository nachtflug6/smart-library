from typer import Argument, echo
from smart_library.application.services.search_service import SearchService
from smart_library.application.models.search_response import SearchResponse, SearchResult, SearchSession
from smart_library.application.services.text_app_service import TextAppService
from smart_library.application.services.document_app_service import DocumentAppService
from smart_library.application.services.entity_app_service import EntityAppService
from smart_library.application.services.ranking_service import RankingService
from smart_library.cli.main import app
import json
from pathlib import Path
from datetime import datetime
from typing import List

SESSION_FILE = Path.cwd() / ".search_session.json"


def _save_session(session: SearchSession):
    """Persist the lightweight SearchSession (query + labels only) to cache."""
    try:
        SESSION_FILE.write_text(json.dumps(session.to_dict(), default=str), encoding="utf-8")
    except Exception as e:
        echo(f"Failed to save search session: {e}")


def _load_session() -> SearchSession:
    """Load the cached SearchSession. Returns empty session if not found."""
    try:
        if not SESSION_FILE.exists():
            return SearchSession(query="")
        data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        return SearchSession.from_dict(data)
    except Exception:
        return SearchSession(query="")


@app.command(name="search")
def search(
    query: str = Argument(..., help="Text to search for"),
    batch_size: int = Argument(10, help="Number of results to show"),
):
    """
    Run a similarity search for `query` and show matching text ids and scores.
    
    Examples:
        smartlib search "xr is useful"    - Search, show first 10 results
        smartlib search "xr is useful" 20 - Search, show first 20 results
    """
    session = _load_session()
    
    # If the query changed, reset labels, offset, and results but keep the new query
    if session.query != query:
        session.query = query
        session.positive_ids.clear()
        session.negative_ids.clear()
        session.offset = 0
        session.results = []
    # If same query, preserve labels and results (allows continued refinement)

    try:
        ranker = RankingService()
        response = ranker.rerank_from_session(
            session=session,
            embedding_service=SearchService().embedding_service,
            text_service=TextAppService(),
            vector_service=SearchService().vector_service,
            top_k=batch_size,
        )
    except Exception as e:
        # fallback to basic similarity search if ranking fails
        try:
            svc = SearchService()
            results = svc.similarity_search(query, top_k=batch_size)
            if not results:
                echo("No results found.")
                return []
            
            # Cache results in session
            session.results = results
            session.offset = 0
            
            # Build response from basic search results
            response = SearchResponse(query=query)
            for i, r in enumerate(results, start=1):
                rid = r.get("id")
                score = r.get("cosine_similarity") or r.get("score") or 0.0
                is_pos = rid in session.positive_ids
                is_neg = rid in session.negative_ids
                response.results.append(SearchResult(rank=i, id=rid, score=score, is_positive=is_pos, is_negative=is_neg))
        except Exception as e2:
            echo(f"Search failed: {e2}")
            return []

    if not response.results:
        echo("No results found.")
        return []

    # Cache results in session
    session.results = [{"id": r.id, "score": r.score} for r in response.results]
    session.offset = 0
    
    # Save the session with cached results
    _save_session(session)

    # Display results using pretty printer if available
    try:
        from smart_library.utils.print import print_search_response
        text_svc = TextAppService()
        doc_svc = DocumentAppService()
        entity_svc = EntityAppService()
        print_search_response(response, text_svc, doc_service=doc_svc, entity_service=entity_svc)
    except Exception:
        # fallback: print minimal numbered results
        for res in response.results:
            echo(f"{res.rank}: {res.id} | score={res.score:.4f}")
    
    return [{"id": r.id, "score": r.score} for r in response.results]


@app.command(name="label")
def label(args: List[str] = Argument(..., help="Identifiers and labels, e.g., '1 2 3 pos 4 5 neg'")):
    """Label search results by rank or ID. Format: identifier(s) followed by pos/neg label.
    
    Examples:
        label 1 pos          - Label result 1 as positive
        label 1 2 3 pos      - Label results 1, 2, 3 as positive
        label 1 2 pos 3 neg  - Label 1, 2 as positive and 3 as negative
    """
    session = _load_session()
    if not session.query:
        echo("No search session found. Run `smartlib search <query>` first.")
        return
    
    # Parse arguments: identifiers followed by label (pos/neg)
    identifiers_to_label = []
    current_identifiers = []
    
    for arg in args:
        if arg in ("pos", "neg"):
            if current_identifiers:
                identifiers_to_label.append((current_identifiers, arg))
                current_identifiers = []
        else:
            current_identifiers.append(arg)
    
    if current_identifiers:
        echo(f"Error: Identifiers {current_identifiers} have no label. Use 'pos' or 'neg'.")
        return
    
    if not identifiers_to_label:
        echo("Error: No valid identifier-label pairs found. Usage: label <id1> <id2>... <pos|neg>")
        return
    
    # Pre-fetch base results once for rank resolution
    base_results = None
    
    # Process each group of identifiers with their label
    labeled_count = 0
    for identifiers, lbl in identifiers_to_label:
        for identifier in identifiers:
            # Determine id from identifier: if numeric -> rank, else assume id
            rid = None
            try:
                rank = int(identifier)
                # Use cached results from session
                if session.results:
                    base_results = session.results
                else:
                    # Fallback: lazy load base results if not cached
                    try:
                        svc = SearchService()
                        base_results = svc.similarity_search(session.query, top_k=50) or []
                    except Exception:
                        base_results = []
                
                if 1 <= rank <= len(base_results):
                    rid = base_results[rank - 1].get("id")
                
                if not rid:
                    echo(f"No result with rank {rank} in last session.")
                    continue
            except ValueError:
                # treat identifier as id
                rid = identifier

            # Update session with the label
            if lbl == "pos":
                session.positive_ids.add(rid)
                session.negative_ids.discard(rid)
            else:  # neg
                session.negative_ids.add(rid)
                session.positive_ids.discard(rid)
            
            labeled_count += 1
    
    if labeled_count > 0:
        _save_session(session)
        echo(f"Labeled {labeled_count} result(s).")
        
        # Automatically re-run and display reranked results after labeling
        try:
            _apply_rerank_and_update_session(echo_results=True)
        except Exception as e:
            # Fail silently if rerank doesn't work
            pass
    else:
        echo("No results were labeled.")

def _apply_rerank_and_update_session(alpha: float = 1.0, beta: float = 0.75, gamma: float = 0.15, top_k: int = 20, echo_results: bool = False):
    """Apply Rocchio reranking using labels from the cached session.
    
    If echo_results is True, print the reranked results to stdout.
    Returns the results list or [] on failure.
    """
    session = _load_session()
    if not session.query:
        if echo_results:
            echo("No search session found. Run `smartlib search <query>` first.")
        return []

    if not session.positive_ids and not session.negative_ids:
        if echo_results:
            echo("No labels found in session. Use `smartlib label <rank> pos|neg` to add labels.")
        return []

    # Call the ranking service with the session
    try:
        ranker = RankingService()
        response = ranker.rerank_from_session(
            session=session,
            embedding_service=SearchService().embedding_service,
            text_service=TextAppService(),
            vector_service=SearchService().vector_service,
            top_k=top_k,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
        )
    except Exception as e:
        if echo_results:
            echo(f"Rerank search failed: {e}")
        return []

    if echo_results:
        try:
            from smart_library.utils.print import print_search_response
            text_svc = TextAppService()
            doc_svc = DocumentAppService()
            entity_svc = EntityAppService()
            print_search_response(response, text_svc, doc_service=doc_svc, entity_service=entity_svc)
        except Exception:
            # Fallback to simple numbered list if pretty printer fails
            echo("Reranked results:")
            for res in response.results:
                echo(f"{res.rank}: {res.id} | score={res.score:.4f}")

    return [{"id": r.id, "score": r.score} for r in response.results]