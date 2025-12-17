from typer import Argument, echo
from smart_library.application.services.search_service import SearchService
from smart_library.application.services.text_app_service import TextAppService
from smart_library.application.services.document_app_service import DocumentAppService
from smart_library.application.services.entity_app_service import EntityAppService
from smart_library.cli.main import app


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

    # Use the boxed visualization if available; fall back to compact lines
    try:
        from smart_library.utils.print import print_search_results_boxed
        text_svc = TextAppService()
        doc_svc = DocumentAppService()
        entity_svc = EntityAppService()
        print_search_results_boxed(results, text_svc, doc_service=doc_svc, entity_service=entity_svc)
    except Exception:
        for r in results:
            rid = r.get("id")
            score = r.get("cosine_similarity") or r.get("cosine") or r.get("score") or 0.0
            echo(f"{rid} | score={score:.4f}")
    return results