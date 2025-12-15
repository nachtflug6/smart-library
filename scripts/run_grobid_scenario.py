#!/usr/bin/env python3
"""Simple scenario: parse a GROBID TEI XML and build a DocumentSnapshot.

Run from repository root:
  PYTHONPATH=src python3 scripts/run_grobid_scenario.py
"""
from pathlib import Path
import sys

from smart_library.infrastructure.grobid.grobid_mapper import GrobidMapper
from smart_library.domain.mappers.grobid_domain.snapshop_mapper import build_snapshot


def main():
    xml_path = Path("data_dev/db/pdf/pdf/Ma2022.xml")
    if not xml_path.exists():
        print(f"XML file not found: {xml_path}")
        sys.exit(2)

    xml = xml_path.read_text(encoding="utf-8")

    mapper = GrobidMapper()
    struct = mapper.xml_to_struct(xml)

    snapshot = build_snapshot(struct, source_path=str(xml_path))

    doc = snapshot.document
    print("Document snapshot created:")
    print("- document id:", getattr(doc, "id", None))
    print("- title:", getattr(doc, "title", None))
    print("- headings:", len(snapshot.headings))
    print("- texts:", len(snapshot.texts))
    print("- relationships:", len(snapshot.relationships))
    print("- terms:", len(snapshot.terms))


if __name__ == "__main__":
    main()
