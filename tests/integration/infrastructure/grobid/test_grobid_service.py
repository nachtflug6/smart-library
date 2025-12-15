import pytest
from pathlib import Path
from smart_library.infrastructure.grobid.grobid_service import GrobidService
from smart_library.infrastructure.grobid.grobid_models import Header, Facsimile, DocumentBody

@pytest.mark.integration
def test_grobid_service_parse_fulltext():
    pdf_path = Path(__file__).parent.parent / "data" / "Ma2022.pdf"
    assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"

    service = GrobidService()
    result = service.parse_fulltext(pdf_path)

    assert isinstance(result, dict)
    assert "header" in result and isinstance(result["header"], Header)
    assert "facsimile" in result and isinstance(result["facsimile"], Facsimile)
    assert "body" in result and isinstance(result["body"], DocumentBody)

    # Optionally, check some fields
    header = result["header"]
    assert header.title is not None
    assert isinstance(header.authors, list)
    print("GrobidService.parse_fulltext output (truncated):")
    print(str(result))