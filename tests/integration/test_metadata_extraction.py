"""Integration tests for metadata extraction with real LLM."""

import pytest
from pathlib import Path

from smart_library.extract.metadata import MetadataExtractor
from smart_library.llm.openai_client import OpenAIClient


@pytest.fixture
def openai_client():
    """Create OpenAI client (requires OPENAI_API_KEY env var)."""
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    return OpenAIClient(api_key=api_key, default_model="gpt-4o-mini", validate_key=False)


@pytest.fixture
def sample_page_chen():
    """Load sample page from ChenZhou2025."""
    # Use relative path from tests directory
    path = Path(__file__).parent.parent / "fixtures/pdf_pages/ChenZhou2025/p01.txt"
    if not path.exists():
        pytest.skip(f"Sample page not found: {path}")
    return path.read_text()


@pytest.fixture
def sample_page_cui():
    """Load sample page from CuiKe2020."""
    # Use relative path from tests directory
    path = Path(__file__).parent.parent / "fixtures/pdf_pages/CuiKe2020/p01.txt"
    if not path.exists():
        pytest.skip(f"Sample page not found: {path}")
    return path.read_text()


def test_extract_single_document_chen(openai_client, sample_page_chen):
    """Test single document extraction with ChenZhou2025 paper."""
    extractor = MetadataExtractor(
        openai_client,
        model="gpt-4o-mini",
        temperature=0.0,
        enforce_json=True,
        debug=True,
    )

    result = extractor.extract([sample_page_chen])

    # Should not have error
    assert "error" not in result

    # Check expected fields
    assert result.get("title") is not None
    assert "Ct-Echo" in result["title"] or "Anomaly Detection" in result["title"]

    # Check authors
    authors = result.get("authors")
    assert authors is not None
    assert isinstance(authors, list)
    assert len(authors) >= 3
    # Should be in "Last, First" format
    assert any("Chen" in a for a in authors)
    assert any("Zhou" in a for a in authors)

    # Check year
    assert result.get("year") == 2025

    # Check venue
    venue = result.get("venue")
    assert venue is not None
    assert "AAAI" in venue

    # Check abstract
    abstract = result.get("abstract")
    assert abstract is not None
    assert len(abstract) > 100


def test_extract_single_document_cui(openai_client, sample_page_cui):
    """Test single document extraction with CuiKe2020 paper."""
    extractor = MetadataExtractor(
        openai_client,
        model="gpt-4o-mini",
        temperature=0.0,
        enforce_json=True,
        debug=True,
    )

    result = extractor.extract([sample_page_cui])

    # Should not have error
    assert "error" not in result

    # Check title
    title = result.get("title")
    assert title is not None
    assert "LSTM" in title or "traffic" in title.lower()

    # Check authors
    authors = result.get("authors")
    assert authors is not None
    assert isinstance(authors, list)
    assert len(authors) >= 4
    # Should contain key authors
    assert any("Cui" in a for a in authors)
    assert any("Ke" in a for a in authors)
    assert any("Wang" in a for a in authors)

    # Check year
    assert result.get("year") == 2020

    # Check venue
    venue = result.get("venue")
    assert venue is not None
    assert "Transportation Research" in venue or "Part C" in venue

    # Check DOI
    doi = result.get("doi")
    if doi:
        assert "10.1016" in doi


def test_extract_bulk_documents(openai_client, sample_page_chen, sample_page_cui):
    """Test bulk extraction of multiple documents."""
    extractor = MetadataExtractor(
        openai_client,
        model="gpt-4o-mini",
        temperature=0.0,
        enforce_json=True,
        debug=False,
    )

    doc_texts = {
        "ChenZhou2025": [sample_page_chen],
        "CuiKe2020": [sample_page_cui],
    }

    results = extractor.extract_bulk(doc_texts, max_pages_per_doc=1)

    # Should have 2 results
    assert len(results) == 2

    # Check document IDs
    doc_ids = {r["document_id"] for r in results}
    assert doc_ids == {"ChenZhou2025", "CuiKe2020"}

    # Check both have valid metadata
    for result in results:
        assert "error" not in result
        assert result.get("title") is not None
        assert result.get("authors") is not None
        assert isinstance(result["authors"], list)
        assert len(result["authors"]) > 0


def test_extract_with_empty_input(openai_client):
    """Test extraction with empty input."""
    extractor = MetadataExtractor(openai_client)
    
    result = extractor.extract([])
    
    assert result == {"error": "no_texts"}


def test_extract_with_missing_fields(openai_client, sample_page_chen):
    """Test that missing fields are normalized to None."""
    extractor = MetadataExtractor(
        openai_client,
        model="gpt-4o-mini",
        temperature=0.0,
        enforce_json=True,
    )

    # Extract from first page only (may miss some fields)
    result = extractor.extract([sample_page_chen[:1000]])

    # Should not error
    assert "error" not in result

    # All expected fields should be present (even if None)
    from smart_library.extract.metadata import EXPECTED_FIELDS
    for field in EXPECTED_FIELDS:
        assert field in result


def test_author_format_normalization(openai_client, sample_page_chen):
    """Test that authors are properly normalized to Last, First format."""
    extractor = MetadataExtractor(
        openai_client,
        model="gpt-4o-mini",
        temperature=0.0,
    )

    result = extractor.extract([sample_page_chen])
    authors = result.get("authors")

    assert authors is not None
    
    # Check format: should be "Last, First" or "Last, First Middle"
    for author in authors:
        assert "," in author, f"Author '{author}' not in 'Last, First' format"
        parts = author.split(",")
        assert len(parts) == 2
        assert parts[0].strip()  # Last name
        assert parts[1].strip()  # First (and possibly middle)


def test_keywords_normalization(openai_client, sample_page_chen):
    """Test that keywords are normalized to lowercase."""
    extractor = MetadataExtractor(
        openai_client,
        model="gpt-4o-mini",
        temperature=0.0,
    )

    result = extractor.extract([sample_page_chen])
    keywords = result.get("keywords")

    if keywords:
        assert isinstance(keywords, list)
        for kw in keywords:
            # Should be lowercase
            assert kw == kw.lower(), f"Keyword '{kw}' not lowercase"