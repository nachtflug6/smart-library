from typer import Argument, echo
from smart_library.application.services.search_service import keyword_search
from smart_library.cli.main import app

@app.command(name="search")
def search(
    query: str = Argument(..., help="Text to search for"),
    what: str = Argument(None, help="Where to search: doc, page, text, term, entities"),
    parent_id: str = Argument(None, help="Parent ID (optional, e.g. document ID for pages, page ID for texts)"),
    top_k: int = Argument(20, help="Maximum number of results to show"),
    window: int = Argument(40, help="Number of characters to show before and after the match"),
):
    """
    Search for text in documents, pages, texts, terms, or all entities (default).
    Shows a snippet of content around the search term.
    Usage:
      smartlib search "deep learning"
      smartlib search "deep learning" doc
      smartlib search "deep learning" page <document_id>
      smartlib search "deep learning" text <page_id>
      smartlib search "deep learning" term
      smartlib search "deep learning" entities [<parent_id>]
    """
    # For now, only keyword search is implemented
    results = keyword_search(query, top_k=top_k, window=window)

    # Optionally filter by 'what' and 'parent_id'
    filtered = []
    for r in results:
        if what and what != "entities" and r["type"] != what.rstrip("s"):
            continue
        if parent_id:
            # Only show results with matching parent_id if available
            parent = r.get("parent_id")
            if parent != parent_id:
                continue
        filtered.append(r)

    if not filtered:
        echo("No results found.")
        return

    for r in filtered:
        echo(f"{r['type'].capitalize()} {r['id']}: {r['snippet']}")