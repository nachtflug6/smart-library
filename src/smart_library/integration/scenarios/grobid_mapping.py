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

    print_scenario_header("GROBID mapping", goal="Map PDF (via Grobid) to domain snapshot")
    print_scenario_table_header(["Document ID", "Title", "Headings", "Texts", "Relationships", "Terms"])
    print_scenario_table_row([
        getattr(doc, "id", None),
        getattr(doc, "title", None),
        len(snapshot.headings),
        len(snapshot.texts),
        len(snapshot.relationships),
        len(snapshot.terms),
    ])

    # Print more document-level info
    print_scenario_table_header(["Doc: Authors", "DOI", "Venue", "Year", "Pages", "Abstract (chars)"])
    abstract_len = len(doc.abstract) if getattr(doc, "abstract", None) else 0
    print_scenario_table_row([
        getattr(doc, "authors", None),
        getattr(doc, "doi", None),
        getattr(doc, "venue", None),
        getattr(doc, "year", None),
        getattr(doc, "page_count", None),
        abstract_len,
    ])
    # Print headings (id, title, index, page_number)
    if snapshot.headings:
        print_scenario_table_header(["Heading ID", "Title", "Index", "Page"])
        for h in snapshot.headings:
            print_scenario_table_row([
                getattr(h, "id", None),
                getattr(h, "title", None),
                getattr(h, "index", None),
                getattr(h, "page_number", None),
            ])

    # Print all texts with small snippets and character counts
    if snapshot.texts:
        print_scenario_table_header(["Text ID", "Type", "Index", "Chars", "Snippet"])
        for t in snapshot.texts:
            content = getattr(t, "display_content", None) or getattr(t, "content", "")
            chars = getattr(t, "character_count", None) or len(content)
            snippet = content.strip().replace("\n", " ")[:200]
            print_scenario_table_row([
                getattr(t, "id", None),
                getattr(t, "text_type", None),
                getattr(t, "index", None),
                chars,
                snippet,
            ])

    # Build lookup maps for headings and texts
    heading_map = {h.id: h for h in snapshot.headings} if snapshot.headings else {}
    text_map = {t.id: t for t in snapshot.texts} if snapshot.texts else {}

    # Print first N relationships
    rels_to_show = snapshot.relationships[:10]
    if rels_to_show:
        print_scenario_table_header(["Source ID", "Target ID", "Type"])
        for r in rels_to_show:
            # Try to include a small hint about the source/target
            src_id = getattr(r, "source_id", None)
            tgt_id = getattr(r, "target_id", None)
            src_snip = None
            tgt_title = None
            if src_id and src_id in text_map:
                src_content = getattr(text_map[src_id], "display_content", None) or getattr(text_map[src_id], "content", "")
                src_snip = src_content.strip().replace("\n", " ")[:120]
            if tgt_id and tgt_id in heading_map:
                tgt_title = getattr(heading_map[tgt_id], "title", None)

            print_scenario_table_row([
                src_id,
                tgt_id,
                getattr(r, "type", None),
            ])
            if src_snip or tgt_title:
                print_scenario_table_row([f"-> src snippet: {src_snip}", f"-> heading: {tgt_title}", "", "", ""])

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
