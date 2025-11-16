import json
from pathlib import Path

import pytest

from smart_library.dataclasses.entities import Entities, Entity
from smart_library.dataclasses.document import Document
from smart_library.dataclasses.page import Page


FIXTURES_ROOT = Path("/workspaces/smart-library/tests/fixtures/documents")
TEXT_DIR = FIXTURES_ROOT / "text"
PDF_DIR = FIXTURES_ROOT / "pdf"


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _iter_pdf_pages(path: Path):
    try:
        import PyPDF2  # type: ignore
    except Exception:
        pytest.skip("PyPDF2 not installed; skipping PDF-based tests")
    reader = PyPDF2.PdfReader(str(path))
    for i, page in enumerate(reader.pages, start=1):
        # extract_text can be None; coerce to empty string
        text = page.extract_text() or ""
        yield i, text


@pytest.fixture
def have_fixtures():
    if not FIXTURES_ROOT.exists():
        pytest.skip(f"Fixture root not found: {FIXTURES_ROOT}")


def build_entities_from_fixtures() -> Entities:
    entities = Entities()

    # Load text documents as single-page
    if TEXT_DIR.exists():
        for txt in sorted(TEXT_DIR.glob("*.txt")):
            doc_id = txt.stem
            content = _read_text_file(txt)
            # document
            entities.add(Entity(
                id=doc_id,
                type="document",
                data={"page_count": 1, "source": str(txt)}
            ))
            # page 1
            entities.add(Entity(
                id=f"{doc_id}_p0001",
                type="page",
                data={
                    "page_number": 1,
                    "page_text": content
                    # document_id will be inferred/filled by Entities
                }
            ))

    # Load PDFs as multi-page (if lib available)
    if PDF_DIR.exists():
        try:
            import PyPDF2  # noqa: F401
            pdf_supported = True
        except Exception:
            pdf_supported = False

        if pdf_supported:
            for pdf in sorted(PDF_DIR.glob("*.pdf")):
                doc_id = pdf.stem
                pages = list(_iter_pdf_pages(pdf))
                page_count = len(pages)

                entities.add(Entity(
                    id=doc_id,
                    type="document",
                    data={"page_count": page_count, "source": str(pdf)}
                ))

                for num, text in pages:
                    entities.add(Entity(
                        id=f"{doc_id}_p{num:04d}",
                        type="page",
                        data={
                            "page_number": num,
                            "page_text": text
                            # document_id will be inferred
                        }
                    ))

    return entities


class TestEntitiesFromDocuments:
    def test_build_and_access(self, have_fixtures):
        entities = build_entities_from_fixtures()

        # We must have at least one document
        docs = entities.get_by_type("document")
        assert len(docs) >= 1

        for doc_entity in docs:
            doc_id = doc_entity.id
            doc = entities.get_document(doc_id)
            assert doc is not None
            assert isinstance(doc, Document)

            page_count = doc_entity.data.get("page_count", 0)
            assert len(doc.pages) == page_count

            # Verify page ids and that page_text is present (may be empty if PDF text extraction fails)
            for idx, page in enumerate(doc.pages, start=1):
                assert isinstance(page, Page)
                assert page.page_number == idx
                ent = entities.get(f"{doc_id}_p{idx:04d}")
                assert ent is not None
                assert ent.type == "page"
                # document_id should be annotated in entity.data
                assert ent.data.get("document_id") == doc_id

    def test_roundtrip_write_and_load(self, tmp_path, have_fixtures):
        entities = build_entities_from_fixtures()

        out = tmp_path / "entities_from_docs.jsonl"
        entities.write(out)
        assert out.exists()

        # Load back and validate a couple of documents
        loaded = Entities.load(out)
        assert len(loaded.get_by_type("document")) == len(entities.get_by_type("document"))
        # pick up to 2 documents to validate
        for doc_entity in loaded.get_by_type("document")[:2]:
            doc_id = doc_entity.id
            page_count = doc_entity.data.get("page_count", 0)
            doc = loaded.get_document(doc_id)
            assert doc is not None
            assert len(doc.pages) == page_count

            # Check first page exists and has a page entity with document_id annotated
            if page_count >= 1:
                first_page_ent = loaded.get(f"{doc_id}_p0001")
                assert first_page_ent is not None
                assert first_page_ent.type == "page"
                assert first_page_ent.data.get("document_id") == doc_id