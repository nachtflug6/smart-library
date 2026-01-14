def print_document(doc, indent=0):
    prefix = " " * indent
    print(f"{prefix}Document: {getattr(doc, 'title', None)} (id={getattr(doc, 'id', None)})")
    print(f"{prefix}  Authors: {getattr(doc, 'authors', None)}")
    print(f"{prefix}  Pages: {len(getattr(doc, 'pages', []))}")

    # Orphan texts: no page_id
    orphan_texts = [t for t in getattr(doc, 'texts', []) if getattr(t, 'page_id', None) is None]
    print(f"{prefix}  Orphan Texts: {len(orphan_texts)}")
    for t in sorted(orphan_texts, key=lambda x: (getattr(x, 'text_type', ''), getattr(x, 'index', -1))):
        if getattr(t, 'text_type', None) == "section":
            print(f"{prefix}    [Orphan Section] {t.title} (index={getattr(t, 'index', None)}, id={getattr(t, 'id', None)})")
        elif getattr(t, 'text_type', None) == "paragraph":
            print(f"{prefix}    [Orphan Paragraph] {repr(t.content)[:120]}... (index={getattr(t, 'index', None)}, id={getattr(t, 'id', None)})")
        else:
            print(f"{prefix}    [Orphan Text] {t.text_type}: {repr(t.content)[:120]}... (index={getattr(t, 'index', None)}, id={getattr(t, 'id', None)})")

    # Print all by page
    for p in sorted(getattr(doc, 'pages', []), key=lambda x: getattr(x, 'page_number', 0)):
        print(f"{prefix}  Page {getattr(p, 'page_number', None)} (id={getattr(p, 'id', None)}):")
        # Get all texts for this page, sorted by index
        page_texts = [t for t in getattr(doc, 'texts', []) if getattr(t, 'page_id', None) == getattr(p, 'id', None)]
        page_sections = [t for t in page_texts if getattr(t, 'text_type', None) == "section"]
        page_paragraphs = [t for t in page_texts if getattr(t, 'text_type', None) == "paragraph"]

        for section in sorted(page_sections, key=lambda x: getattr(x, 'index', -1)):
            print(f"{prefix}    [Section] {section.title} (index={getattr(section, 'index', None)}, id={getattr(section, 'id', None)})")
            # Print paragraphs under this section, sorted by index
            section_paragraphs = [para for para in page_paragraphs if getattr(para, 'parent_id', None) == getattr(section, 'id', None)]
            for para in sorted(section_paragraphs, key=lambda x: getattr(x, 'index', -1)):
                print(f"{prefix}      [Paragraph] {repr(para.content)}... (index={getattr(para, 'index', None)}, id={getattr(para, 'id', None)})")
        # Print paragraphs not under any section
        unsectioned_paragraphs = [para for para in page_paragraphs if getattr(para, 'parent_id', None) not in [getattr(s, 'id', None) for s in page_sections]]
        for para in sorted(unsectioned_paragraphs, key=lambda x: getattr(x, 'index', -1)):
            print(f"{prefix}    [Paragraph] {repr(para.content)}... (index={getattr(para, 'index', None)}, id={getattr(para, 'id', None)})")


def print_search_results_boxed(results, text_service, doc_service=None, entity_service=None, max_chars=None):
    """Print each search result in its own boxed table.

    results: iterable of dict-like objects with keys `id` and `cosine_similarity` (or `cosine`)
    services: service objects that expose `.get_text(id)` and `.get_document(id)`.
    The `max_chars` defaults to `ChunkerConfig.MAX_CHAR` from config.
    """
    from smart_library.config import ChunkerConfig
    from tabulate import tabulate

    max_chars = max_chars or ChunkerConfig.MAX_CHAR

    def _truncate_text(text: str, max_c: int) -> str:
        if text is None:
            return ""
        text = str(text).strip().replace("\n", " ")
        if len(text) <= max_c:
            return text
        return text[: max_c - 3].rstrip() + "..."

    def _get_attr(obj, name, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    import textwrap

    # Compact mode: single-line metadata header + wrapped snippet
    for r in results or []:
        tid = r.get("id") if isinstance(r, dict) else getattr(r, "id", None)
        score = (r.get("cosine_similarity") or r.get("cosine")) if isinstance(r, dict) else getattr(r, "cosine_similarity", None) or getattr(r, "cosine", 0.0)
        score = float(score or 0.0)

        txt = text_service.get_text(tid) if text_service else None
        content = _get_attr(txt, "content", None) or _get_attr(txt, "display_content", "")
        metadata = _get_attr(txt, "metadata", {}) or {}
        page = _get_attr(txt, "page_number", None) or metadata.get("page_number") or metadata.get("page") or metadata.get("page_num") or ""
        parent_id = _get_attr(txt, "parent_id", None) or metadata.get("parent_id")

        # Resolve document title/author/year
        doc = None
        if entity_service and parent_id:
            try:
                parent = entity_service.get(parent_id)
                if parent:
                    p_parent = parent.get("parent_id") if isinstance(parent, dict) else getattr(parent, "parent_id", None)
                    doc_id = p_parent or (parent.get("id") if isinstance(parent, dict) else getattr(parent, "id", None))
                    doc = doc_service.get_document(doc_id) if doc_service and doc_id else None
            except Exception:
                doc = None
        elif doc_service and parent_id:
            try:
                doc = doc_service.get_document(parent_id)
            except Exception:
                doc = None

        title = _get_attr(doc, "title", "")
        authors = _get_attr(doc, "authors", []) or []
        first_author = authors[0] if isinstance(authors, (list, tuple)) and authors else (authors if isinstance(authors, str) else "")
        year = _get_attr(doc, "year", "")

        # Compact header
        short_title = title if len(title) <= 60 else title[:57].rstrip() + "..."
        header = f"{short_title} — {first_author + ' et al.' if first_author else ''} — {year} — p{page} — score={score:.4f}"
        # Very compact: single-line header + single-line truncated snippet
        snippet = _truncate_text(content or "", max_chars or 140)
        print(header)
        print("  " + snippet)
        # separator between results
        print("\n" + ("-" * 80) + "\n")


def print_search_response(response, text_service, doc_service=None, entity_service=None, max_chars=None):
    """Print a SearchResponse object in a readable format.

    response: object with attributes `query`, `created_at`, `results` (iterable of objects with
    `rank`, `id`, `score`, `is_positive`, `is_negative`).
    """
    from smart_library.config import ChunkerConfig

    max_chars = max_chars or ChunkerConfig.MAX_CHAR

    def _truncate_text(text: str, max_c: int) -> str:
        if text is None:
            return ""
        text = str(text).strip().replace("\n", " ")
        if len(text) <= max_c:
            return text
        return text[: max_c - 3].rstrip() + "..."

    def _get_attr(obj, name, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    print(f"Search: {getattr(response, 'query', '')} — {getattr(response, 'created_at', '')}")
    print(f"Results: {len(getattr(response, 'results', []) or [])}\n")

    summary_rows = []
    # Build a compact table: rank, id, title, author(year), page, score, snippet
    table_rows = []
    for r in getattr(response, "results", []) or []:
        tid = r.id if not isinstance(r, dict) else r.get("id")
        score = (getattr(r, "score", None) if not isinstance(r, dict) else r.get("score")) or 0.0

        txt = text_service.get_text(tid) if text_service else None
        content = _get_attr(txt, "content", None) or _get_attr(txt, "display_content", "")
        metadata = _get_attr(txt, "metadata", {}) or {}
        page = _get_attr(txt, "page_number", None) or metadata.get("page_number") or metadata.get("page") or metadata.get("page_num") or ""
        parent_id = _get_attr(txt, "parent_id", None) or metadata.get("parent_id")

        # Resolve document title/author/year
        doc = None
        if entity_service and parent_id:
            try:
                parent = entity_service.get(parent_id)
                if parent:
                    p_parent = parent.get("parent_id") if isinstance(parent, dict) else getattr(parent, "parent_id", None)
                    doc_id = p_parent or (parent.get("id") if isinstance(parent, dict) else getattr(parent, "id", None))
                    doc = doc_service.get_document(doc_id) if doc_service and doc_id else None
            except Exception:
                doc = None
        elif doc_service and parent_id:
            try:
                doc = doc_service.get_document(parent_id)
            except Exception:
                doc = None

        title = _get_attr(doc, "title", "")
        authors = _get_attr(doc, "authors", []) or []
        first_author = authors[0] if isinstance(authors, (list, tuple)) and authors else (authors if isinstance(authors, str) else "")
        year = _get_attr(doc, "year", "")

        display_id = None
        if doc is not None:
            display_id = _get_attr(doc, "human_id") or _get_attr(doc, "citation_key") or _get_attr(doc, "id")
        display_id = display_id or tid

        # Use full title and snippet; wrapping will handle long text when printing
        snippet_full = content or ""
        author_year = f"{first_author} ({year})" if first_author or year else ""
        title_full = title or ""

        table_rows.append((r.rank, display_id, title_full, author_year, page, f"{float(score):.4f}", snippet_full))

    # Print results in a 2-3 row wrapped layout: header (rank, id), title line, meta line, then wrapped snippet
    try:
        import shutil
        term_w = shutil.get_terminal_size((120, 20)).columns
    except Exception:
        term_w = 120

    import textwrap
    indent = "  "
    for row in table_rows:
        rank = row[0]
        display_id = row[1]
        title = row[2]
        author_year = row[3]
        page = row[4]
        score = row[5]
        snippet = row[6]

        # Prepare width and separators
        sep = " | "
        prefix = f"{rank}."
        id_repr = f"[{display_id}]"
        avail = max(40, term_w - len(indent))

        # Build suffix pieces (author, page)
        suffix_parts = []
        if author_year:
            suffix_parts.append(author_year)
        if page:
            suffix_parts.append(f"p{page}")
        suffix = sep.join(suffix_parts) if suffix_parts else ""

        # Format score (3 significant digits) and place it after rank
        try:
            score_val = float(score)
        except Exception:
            score_val = 0.0
        score_fmt = f"{score_val:.3g}"

        # Lead: rank, score, id, page; Trail: author_year
        page_part = f"p{page}" if page else ""
        # Build lead dynamically including page if present
        if page_part:
            lead = f"{prefix} {score_fmt}{sep}{id_repr}{sep}{page_part}{sep}"
        else:
            lead = f"{prefix} {score_fmt}{sep}{id_repr}{sep}"
        trail = f"{sep}{author_year}" if author_year else ""

        # Compute allowed title width and truncate if necessary
        title_display = str(title) if title else ""
        allowed_for_title = avail - (len(lead) + len(trail))
        if allowed_for_title <= 0:
            # no room for title, show lead only (and trail if fits)
            meta_line = lead.rstrip(sep)
            if trail and len(meta_line) + len(trail) <= avail:
                meta_line = meta_line + trail
        else:
            if len(title_display) > allowed_for_title:
                title_display = title_display[: max(0, allowed_for_title - 3)].rstrip() + "..."
            meta_line = lead + title_display + trail

        # Final safety: ensure meta_line not longer than avail
        if len(meta_line) > avail:
            meta_line = meta_line[: max(0, avail - 3)].rstrip() + "..."

        print(indent + meta_line)

        # Dashed separator after metadata line (exact terminal width)
        print("=" * term_w)

        # Snippet: wrapped text on following lines (no truncation)
        snippet_wrapped = textwrap.fill(str(snippet), width=term_w - len(indent), subsequent_indent=indent)
        print(indent + snippet_wrapped)

        # Equals separator between results (exact terminal width)
        print("=" * term_w)

        # Blank line after equals separator
        print()