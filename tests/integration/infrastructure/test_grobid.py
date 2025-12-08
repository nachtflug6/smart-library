import pytest
from pathlib import Path
from smart_library.infrastructure.grobid.client import GrobidClient
from smart_library.infrastructure.grobid.mapper import GrobidMapper

@pytest.mark.integration
def test_grobid_extract_fulltext():
    pdf_path = Path(__file__).parent.parent / "data" / "Ma2022.pdf"
    assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"

    client = GrobidClient()
    fulltext = client.extract_fulltext(pdf_path)

    assert isinstance(fulltext, str)
    assert "<TEI" in fulltext  # Grobid returns TEI XML
    assert len(fulltext) > 100  # Should not be empty

    print("Grobid fulltext extraction output (truncated):")
    print(fulltext[:500])

@pytest.mark.integration
def test_grobid_extract_header():
    pdf_path = Path(__file__).parent.parent / "data" / "Ma2022.pdf"
    assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"

    client = GrobidClient()
    header = client.extract_header(pdf_path)

    assert isinstance(header, str)
    assert header.startswith("@") or "<TEI" in header
    assert len(header) > 50  # Should not be empty

    print("Grobid header extraction output (truncated):")
    print(header[:500])

import pytest
from pathlib import Path
from smart_library.infrastructure.grobid.client import GrobidClient
from smart_library.infrastructure.grobid.mapper import GrobidMapper

@pytest.mark.integration
def test_grobid_mapper_headers_to_dict():
    pdf_path = Path(__file__).parent.parent / "data" / "Ma2022.pdf"
    assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"

    client = GrobidClient()
    header_xml = client.extract_header(pdf_path)

    # Only test if we got TEI XML, otherwise skip (BibTeX etc. is not supported by the mapper)
    if not header_xml.lstrip().startswith("<"):
        pytest.skip("Header extraction did not return TEI XML, skipping mapper test.")

    mapper = GrobidMapper()
    result = mapper.headers_to_dict(header_xml)

    assert isinstance(result, dict)
    assert "metadata" in result
    assert "title" in result["metadata"]
    assert "authors" in result["metadata"]
    assert "text_blocks" in result
    print("GrobidMapper.headers_to_dict output (truncated):")
    print(str(result)[:500])