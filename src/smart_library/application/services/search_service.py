from smart_library.application.services.list_service import ListingService
import re

def get_context_snippet(text, query, window=40):
    """Return a snippet of text around the first occurrence of query."""
    if not text:
        return ""
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""
    start = max(match.start() - window, 0)
    end = min(match.end() + window, len(text))
    snippet = text[start:end]
    # Optionally highlight the match (remove ANSI if not needed)
    snippet = pattern.sub(lambda m: f"[{m.group(0)}]", snippet)
    return f"...{snippet}..."

def keyword_search(query: str, top_k: int = 20, window: int = 40):
    """
    Keyword search across documents, pages, chunks, and terms.
    Returns a list of dicts with type, id, and snippet.
    """
    service = ListingService()
    results = []

    # Search documents
    docs = service.list_documents()
    for doc in docs:
        for field in ("title", "doi", "authors", "metadata"):
            val = getattr(doc, field, "")
            if query.lower() in str(val).lower():
                snippet = get_context_snippet(str(val), query, window=window)
                results.append({"type": "document", "id": doc.id, "snippet": snippet})
                break  # Only add each doc once

    # Search pages
    pages = service.repo_page.list()
    for page in pages:
        val = getattr(page, "full_text", "")
        if query.lower() in str(val).lower():
            snippet = get_context_snippet(val, query, window=window)
            results.append({"type": "page", "id": page.id, "snippet": snippet})

    # Search chunks/texts
    texts = service.repo_text.list()
    for text in texts:
        val = getattr(text, "content", "")
        if query.lower() in str(val).lower():
            snippet = get_context_snippet(val, query, window=window)
            results.append({"type": "text", "id": text.id, "snippet": snippet})

    # Search terms
    terms = service.repo_term.list()
    for term in terms:
        val = getattr(term, "name", "")
        if query.lower() in str(val).lower():
            snippet = get_context_snippet(val, query, window=window)
            results.append({"type": "term", "id": term.id, "snippet": snippet})

    # Return top_k results
    return results[:top_k]

# You can implement semantic_search, hybrid_search, etc. similarly.
