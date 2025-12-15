#!/usr/bin/env python3
"""Simple scenario: parse a GROBID TEI XML and build a DocumentSnapshot.

Run from repository root:
  PYTHONPATH=src python3 scripts/run_grobid_scenario.py
"""
from pathlib import Path
import sys
import traceback

from smart_library.infrastructure.grobid.grobid_mapper import GrobidMapper
from smart_library.domain.mappers.grobid_domain.snapshop_mapper import build_snapshot
from smart_library.integration.scenarios.utils import (
    print_scenario_header,
    print_scenario_footer,
    print_scenario_table_header,
    print_scenario_table_row,
)

from smart_library.config import DATA_DIR


def scenario_xml_to_domain(context=None):
    xml_path = DATA_DIR / "pdf" / "huizhong_test.xml"
    if not xml_path.exists():
        raise FileNotFoundError(f"XML file not found: {xml_path}")

    xml = xml_path.read_text(encoding="utf-8")

    mapper = GrobidMapper()
    struct = mapper.xml_to_struct(xml)

    snapshot = build_snapshot(struct, source_path=str(xml_path))

    doc = snapshot.document

    print_scenario_header("GROBID mapping", goal="Map TEI XML to domain snapshot")
    print_scenario_table_header(["Document ID", "Title", "Headings", "Texts", "Relationships", "Terms"])
    print_scenario_table_row([
        getattr(doc, "id", None),
        getattr(doc, "title", None),
        len(snapshot.headings),
        len(snapshot.texts),
        len(snapshot.relationships),
        len(snapshot.terms),
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

    # Print first N relationships
    rels_to_show = snapshot.relationships[:10]
    if rels_to_show:
        print_scenario_table_header(["Source ID", "Target ID", "Type"])
        for r in rels_to_show:
            print_scenario_table_row([
                getattr(r, "source_id", None),
                getattr(r, "target_id", None),
                getattr(r, "type", None),
            ])

    print_scenario_footer()


def main():
    try:
        scenario_xml_to_domain(None)
    except Exception:
        # Print a full traceback and some helpful contextual info
        print("Error running Grobid mapping scenario:\n", file=sys.stderr)
        traceback.print_exc()
        xml_path = DATA_DIR / "pdf" / "huizhong_test.xml"
        print(f"\nContext:\n - XML path: {xml_path}\n - exists: {xml_path.exists()}\n - DATA_DIR: {DATA_DIR}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
