"""Unit tests for smart_library.ingest.onboard module."""
import pytest
import shutil
from pathlib import Path
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from unittest.mock import patch

from smart_library.ingest.onboard import (
    onboard_document,
    onboard_pages,
    onboard_documents,
)
from smart_library.utils.jsonl import read_jsonl


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    """Create temporary config paths for testing."""
    doc_pdf_dir = tmp_path / "documents" / "pdf"
    doc_text_dir = tmp_path / "documents" / "text"
    entities_jsonl = tmp_path / "entities.jsonl"
    
    # Patch the config module
    monkeypatch.setattr("smart_library.config.DOC_PDF_DIR", doc_pdf_dir)
    monkeypatch.setattr("smart_library.config.DOC_TEXT_DIR", doc_text_dir)
    monkeypatch.setattr("smart_library.config.ENTITIES_JSONL", entities_jsonl)
    
    # Also patch in the onboard module
    monkeypatch.setattr("smart_library.ingest.onboard.DOC_PDF_DIR", doc_pdf_dir)
    monkeypatch.setattr("smart_library.ingest.onboard.DOC_TEXT_DIR", doc_text_dir)
    monkeypatch.setattr("smart_library.ingest.onboard.ENTITIES_JSONL", entities_jsonl)
    
    print(f"\n[fixture] Temporary config paths:")
    print(f"[fixture] DOC_PDF_DIR: {doc_pdf_dir}")
    print(f"[fixture] DOC_TEXT_DIR: {doc_text_dir}")
    print(f"[fixture] ENTITIES_JSONL: {entities_jsonl}")
    
    return {
        "doc_pdf_dir": doc_pdf_dir,
        "doc_text_dir": doc_text_dir,
        "entities_jsonl": entities_jsonl,
    }


@pytest.fixture
def temp_pdf(tmp_path):
    """Create a temporary test PDF with 3 pages."""
    pdf_path = tmp_path / "test_document.pdf"
    
    writer = PdfWriter()
    
    # Create 3 pages with different content
    for page_num in range(1, 4):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(100, 750, f"Test Document - Page {page_num}")
        can.drawString(100, 700, f"This is page {page_num} content.")
        can.save()
        packet.seek(0)
        
        reader = PdfReader(packet)
        writer.add_page(reader.pages[0])
    
    with open(pdf_path, "wb") as f:
        writer.write(f)
    
    print(f"\n[fixture] Created test PDF: {pdf_path}")
    
    yield pdf_path


@pytest.fixture
def temp_pdfs(tmp_path):
    """Create multiple temporary test PDFs."""
    pdfs = []
    for i in range(1, 3):
        pdf_path = tmp_path / f"doc_{i}.pdf"
        
        writer = PdfWriter()
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(100, 750, f"Document {i}")
        can.save()
        packet.seek(0)
        
        reader = PdfReader(packet)
        writer.add_page(reader.pages[0])
        
        with open(pdf_path, "wb") as f:
            writer.write(f)
        
        pdfs.append(pdf_path)
        print(f"\n[fixture] Created test PDF {i}: {pdf_path}")
    
    yield pdfs


def test_onboard_document_basic(temp_pdf, temp_config):
    """Test basic document onboarding."""
    print(f"\n[test] Onboarding PDF: {temp_pdf}")
    
    doc_id = onboard_document(temp_pdf, label="Test Document")
    
    print(f"[test] Document ID: {doc_id}")
    assert doc_id == f"doc:{temp_pdf.stem}"
    
    # Check PDF was copied
    dest_pdf = temp_config["doc_pdf_dir"] / temp_pdf.name
    print(f"[test] Destination PDF: {dest_pdf}")
    assert dest_pdf.exists()
    
    # Check entities were created
    entities = read_jsonl(temp_config["entities_jsonl"])
    by_id = {e["id"]: e for e in entities}
    
    print(f"[test] Total entities: {len(entities)}")
    
    # Check document entity
    assert doc_id in by_id
    doc_entity = by_id[doc_id]
    
    assert doc_entity["type"] == "document"
    assert doc_entity["label"] == "Test Document"
    assert doc_entity["data"]["page_count"] == 3
    
    # Check page entities
    page_ids = [f"page:{temp_pdf.stem}:{i:02d}" for i in range(1, 4)]
    for page_id in page_ids:
        assert page_id in by_id
        page_entity = by_id[page_id]
        assert page_entity["type"] == "page"
        assert page_entity["data"]["document_id"] == doc_id
        
        text_path = Path(page_entity["data"]["text_path"])
        assert text_path.exists()


def test_onboard_document_without_label(temp_pdf, temp_config):
    """Test onboarding without explicit label."""
    doc_id = onboard_document(temp_pdf)
    
    entities = read_jsonl(temp_config["entities_jsonl"])
    by_id = {e["id"]: e for e in entities}
    
    assert by_id[doc_id]["label"] == temp_pdf.stem


def test_onboard_document_file_not_found(temp_config):
    """Test error handling for non-existent file."""
    with pytest.raises(FileNotFoundError):
        onboard_document("/path/to/nonexistent.pdf")


def test_onboard_document_not_pdf(tmp_path, temp_config):
    """Test error handling for non-PDF file."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Not a PDF")
    
    with pytest.raises(ValueError, match="Not a PDF file"):
        onboard_document(txt_file)


def test_onboard_document_update_existing(temp_pdf, temp_config):
    """Test updating an existing document."""
    doc_id = onboard_document(temp_pdf, label="Original Label")
    entities_v1 = read_jsonl(temp_config["entities_jsonl"])
    by_id_v1 = {e["id"]: e for e in entities_v1}
    
    doc_id_2 = onboard_document(temp_pdf, label="Updated Label")
    
    assert doc_id == doc_id_2
    
    entities_v2 = read_jsonl(temp_config["entities_jsonl"])
    by_id_v2 = {e["id"]: e for e in entities_v2}
    
    assert by_id_v2[doc_id]["label"] == "Updated Label"


def test_onboard_pages_only(temp_pdf, temp_config):
    """Test re-extracting pages for existing document."""
    onboard_document(temp_pdf)
    
    entities = read_jsonl(temp_config["entities_jsonl"])
    by_id = {e["id"]: e for e in entities}
    
    page_id = f"page:{temp_pdf.stem}:01"
    
    onboard_pages(document_ids=[temp_pdf.stem])
    
    entities_v2 = read_jsonl(temp_config["entities_jsonl"])
    by_id_v2 = {e["id"]: e for e in entities_v2}
    
    assert Path(by_id_v2[page_id]["data"]["text_path"]).exists()


def test_onboard_pages_with_none(temp_pdf, temp_config):
    """Test that onboard_pages does nothing with None input."""
    onboard_document(temp_pdf)
    
    entities_before = read_jsonl(temp_config["entities_jsonl"])
    onboard_pages(document_ids=None)
    entities_after = read_jsonl(temp_config["entities_jsonl"])
    
    assert len(entities_before) == len(entities_after)


def test_onboard_pages_with_empty_list(temp_pdf, temp_config):
    """Test that onboard_pages does nothing with empty list."""
    onboard_document(temp_pdf)
    
    entities_before = read_jsonl(temp_config["entities_jsonl"])
    onboard_pages(document_ids=[])
    entities_after = read_jsonl(temp_config["entities_jsonl"])
    
    assert len(entities_before) == len(entities_after)


def test_onboard_documents_multiple(temp_pdfs, temp_config):
    """Test onboarding multiple documents at once."""
    doc_ids = onboard_documents(temp_pdfs)
    
    assert len(doc_ids) == len(temp_pdfs)
    
    entities = read_jsonl(temp_config["entities_jsonl"])
    by_id = {e["id"]: e for e in entities}
    
    for doc_id in doc_ids:
        assert doc_id in by_id
        assert by_id[doc_id]["type"] == "document"


def test_onboard_documents_with_invalid_file(temp_pdfs, tmp_path, temp_config):
    """Test that onboard_documents skips invalid files."""
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("Not a PDF")
    
    all_files = temp_pdfs + [invalid_file]
    doc_ids = onboard_documents(all_files)
    
    assert len(doc_ids) == len(temp_pdfs)


def test_page_text_content(temp_pdf, temp_config):
    """Test that extracted page text contains expected content."""
    doc_id = onboard_document(temp_pdf)
    stem = temp_pdf.stem
    
    entities = read_jsonl(temp_config["entities_jsonl"])
    by_id = {e["id"]: e for e in entities}
    
    page_id = f"page:{stem}:01"
    text_path = Path(by_id[page_id]["data"]["text_path"])
    text_content = text_path.read_text()
    
    assert "Test Document - Page 1" in text_content
    assert "This is page 1 content" in text_content


def test_document_directory_structure(temp_pdf, temp_config):
    """Test that directory structure is created correctly."""
    doc_id = onboard_document(temp_pdf)
    stem = temp_pdf.stem
    
    assert temp_config["doc_pdf_dir"].exists()
    assert (temp_config["doc_pdf_dir"] / temp_pdf.name).exists()
    
    doc_text_dir = temp_config["doc_text_dir"] / stem
    assert doc_text_dir.exists()
    
    for i in range(1, 4):
        page_file = doc_text_dir / f"p{i:02d}.txt"
        assert page_file.exists()