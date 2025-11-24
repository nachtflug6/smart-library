import pytest
from unittest.mock import patch, MagicMock
from smart_library.application.pdf.pdf_reader import PDFReader

def test_read_returns_page_texts(monkeypatch):
    mock_pdf = MagicMock()
    mock_page1 = MagicMock()
    mock_page2 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1 text"
    mock_page2.extract_text.return_value = "Page 2 text"
    mock_pdf.pages = [mock_page1, mock_page2]

    # Patch pypdf.PdfReader to return our mock
    monkeypatch.setattr("pypdf.PdfReader", lambda f: mock_pdf)
    reader = PDFReader()
    # Patch open to avoid file IO
    with patch("builtins.open", MagicMock()):
        result = reader.read("dummy.pdf")
    assert result == ["Page 1 text", "Page 2 text"]

def test_read_file_not_found():
    reader = PDFReader()
    with pytest.raises(FileNotFoundError):
        reader.read("nonexistent.pdf")

def test_read_pdf_error(monkeypatch):
    # Patch pypdf.PdfReader to raise an error
    monkeypatch.setattr("pypdf.PdfReader", lambda f: (_ for _ in ()).throw(Exception("bad pdf")))
    reader = PDFReader()
    with patch("builtins.open", MagicMock()):
        with pytest.raises(ValueError) as excinfo:
            reader.read("dummy.pdf")
        assert "Failed to read PDF" in str(excinfo.value)