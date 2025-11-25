# smart_library/application/services/search_service.py

def search(query: str, mode: str = "auto", top_k: int = 20):
    """
    Main search method.
    mode: auto | keyword | semantic | documents | pages | chunks | terms
    """
    # You will implement these functions later
    if mode == "keyword":
        return keyword_search(query, top_k)
    if mode == "semantic":
        return semantic_search(query, top_k)
    if mode == "documents":
        return search_documents(query, top_k)
    if mode == "pages":
        return search_pages(query, top_k)
    if mode == "chunks":
        return search_chunks(query, top_k)
    if mode == "terms":
        return search_terms(query, top_k)

    # Default: auto mode
    return hybrid_search(query, top_k)
