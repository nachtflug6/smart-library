#!/usr/bin/env python3
"""Simple scenario: parse a GROBID TEI XML and build a DocumentSnapshot.

Run from repository root:
  PYTHONPATH=src python3 scripts/run_grobid_scenario.py
"""
from pathlib import Path
import sys
import traceback

from smart_library.infrastructure.grobid.grobid_service import GrobidService
from smart_library.domain.mappers.grobid_domain.snapshop_mapper import build_snapshot
from smart_library.integration.scenarios.utils import (
    print_scenario_header,
    print_scenario_footer,
    print_scenario_table_header,
    print_scenario_table_row,
)

from smart_library.config import DATA_DIR


def scenario_pdf_to_domain(context=None, pdf_path=None):
    """Map a PDF to a domain snapshot using Grobid extraction.

    Always extracts TEI via the `GrobidService` from a PDF. If `pdf_path`
    is not provided, the default `DATA_DIR/pdf/huizhong_test.pdf` is used.
    Returns the built `DocumentSnapshot`.
    """
    if pdf_path is None:
        pdf_path = DATA_DIR / "pdf" / "huizhong_test.pdf"

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    service = GrobidService()
    struct = service.extract_fulltext(pdf_path)
    snapshot = build_snapshot(struct, source_path=str(pdf_path))

    doc = snapshot.document

    def _short_id(val, length=4):
        if val is None:
            return ""
        s = str(val)
        return s[:length]

    def _short_text(val, length=80):
        if not val:
            return ""
        s = str(val).strip()
        if len(s) <= length:
            return s
        return s[: length - 3].rstrip() + "..."

    def _format_authors(authors, max_authors=3):
        if not authors:
            return ""
        try:
            if isinstance(authors, (list, tuple)):
                if len(authors) <= max_authors:
                    return ", ".join(authors)
                return ", ".join(authors[:max_authors]) + ", et al."
            return str(authors)
        except Exception:
            return str(authors)

    print_scenario_header("GROBID mapping", goal="Map PDF (via Grobid) to domain snapshot")
    print_scenario_table_header(["Document ID", "Title", "Headings", "Texts", "Relationships", "Terms"])
    print_scenario_table_row([
        _short_id(getattr(doc, "id", None)),
        _short_text(getattr(doc, "title", None), length=80),
        len(snapshot.headings),
        len(snapshot.texts),
        len(snapshot.relationships),
        len(snapshot.terms),
    ])

    # limit displayed items per category
    MAX_SHOW = 10

    # Print more document-level info
    print_scenario_table_header(["Doc: Authors", "DOI", "Venue", "Year", "Pages", "Abstract (chars)"])
    abstract_len = len(doc.abstract) if getattr(doc, "abstract", None) else 0
    print_scenario_table_row([
        _format_authors(getattr(doc, "authors", None)),
        getattr(doc, "doi", None),
        getattr(doc, "venue", None),
        getattr(doc, "year", None),
        getattr(doc, "page_count", None),
        abstract_len,
    ])
    # Print headings (id, title, index, page_number)
    if snapshot.headings:
        total_headings = len(snapshot.headings)
        print_scenario_table_header(["Heading ID", "Title", "Index", "Page"])
        for h in snapshot.headings[:MAX_SHOW]:
            page = getattr(h, "page_number", None)
            page_display = "" if (page is None or page == 0) else page
            print_scenario_table_row([
                _short_id(getattr(h, "id", None)),
                _short_text(getattr(h, "title", None), length=60),
                getattr(h, "index", None) if getattr(h, "index", None) is not None else "",
                page_display,
            ])
        if total_headings > MAX_SHOW:
            remaining = total_headings - MAX_SHOW
            print_scenario_table_row([f"... and {remaining} more", "", "", ""])

    # Print all texts with small snippets and character counts
    if snapshot.texts:
        total_texts = len(snapshot.texts)
        print_scenario_table_header(["Text ID", "Type", "Index", "Chars", "Snippet"])
        for t in snapshot.texts[:MAX_SHOW]:
            content = getattr(t, "display_content", None) or getattr(t, "content", "")
            chars = getattr(t, "character_count", None) or len(content)
            snippet = content.strip().replace("\n", " ")[:80]
            print_scenario_table_row([
                _short_id(getattr(t, "id", None)),
                getattr(t, "text_type", None),
                getattr(t, "index", None),
                chars,
                snippet,
            ])
        if total_texts > MAX_SHOW:
            print_scenario_table_row([f"... and {total_texts - MAX_SHOW} more", "", "", "", ""])

    # Build lookup maps for headings and texts
    heading_map = {h.id: h for h in snapshot.headings} if snapshot.headings else {}
    text_map = {t.id: t for t in snapshot.texts} if snapshot.texts else {}

    # Print first N relationships (compact: one row per relationship)
    rels_to_show = snapshot.relationships
    if rels_to_show:
        total_rels = len(rels_to_show)
        print_scenario_table_header(["Source", "Target", "Type", "Snippet", "Heading"])
        for r in rels_to_show[:MAX_SHOW]:
            src_id = getattr(r, "source_id", None)
            tgt_id = getattr(r, "target_id", None)
            rel_type = getattr(r, "type", None)

            src_snip = ""
            if src_id and src_id in text_map:
                src_content = getattr(text_map[src_id], "display_content", None) or getattr(text_map[src_id], "content", "")
                src_snip = src_content.strip().replace("\n", " ")[:60]

            tgt_title = ""
            if tgt_id and tgt_id in heading_map:
                tgt_title = (getattr(heading_map[tgt_id], "title", None) or "")[:30]

            print_scenario_table_row([
                _short_id(src_id),
                _short_id(tgt_id),
                rel_type or "",
                src_snip,
                tgt_title,
            ])
        if total_rels > MAX_SHOW:
            print_scenario_table_row([f"... and {total_rels - MAX_SHOW} more", "", "", "", ""])

    print_scenario_footer()
    return snapshot


def main():
    try:
        # Allow passing a PDF path as first arg to run mapping directly from PDF
        pdf_arg = None
        if len(sys.argv) > 1:
            pdf_arg = sys.argv[1]
        scenario_pdf_to_domain(None, pdf_path=pdf_arg)
    except Exception:
        # Print a full traceback and some helpful contextual info
        print("Error running Grobid mapping scenario:\n", file=sys.stderr)
        traceback.print_exc()
        default_pdf = DATA_DIR / "pdf" / "huizhong_test.pdf"
        print(
            f"\nContext:\n - default PDF path: {default_pdf}\n - exists: {default_pdf.exists()}\n - DATA_DIR: {DATA_DIR}\n - argv: {sys.argv}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
