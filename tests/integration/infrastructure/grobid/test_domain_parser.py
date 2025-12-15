import pytest
from pathlib import Path
from smart_library.infrastructure.grobid.service import GrobidService
from smart_library.infrastructure.parsers.document import parse_document
from smart_library.domain.entities.document import Document
from smart_library.domain.entities.page import Page
from smart_library.domain.entities.text import Text
from smart_library.utils.print import print_document

@pytest.mark.integration
def test_tei_domain_parser_from_grobid_struct():
    pdf_path = Path(__file__).parent.parent / ".." / "data" / "pdf" / "Ma2022.pdf"
    assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"

    service = GrobidService()
    grobid_struct = service.parse_fulltext(pdf_path)

    doc = parse_document(grobid_struct, source_path=str(pdf_path))

    assert isinstance(doc, Document)
    assert isinstance(doc.pages, list)
    assert all(isinstance(p, Page) for p in doc.pages)
    assert isinstance(doc.texts, list)
    assert all(isinstance(t, Text) for t in doc.texts)
    assert doc.title is not None
    assert isinstance(doc.authors, list)

    # Check orphan texts: parent_id == doc.id
    orphan_texts = [t for t in doc.texts if getattr(t, "parent_id", None) == getattr(doc, "id", None)]
    print(f"Orphan texts count: {len(orphan_texts)}")
    for t in orphan_texts:
        print(f"Orphan text: {t.text_type}, id={getattr(t, 'id', None)}, content={repr(t.content)[:60]}...")

    print("tei_domain_parser output (truncated):")
    print_document(doc)