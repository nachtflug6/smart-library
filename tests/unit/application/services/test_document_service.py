import pytest
from unittest.mock import Mock
from datetime import datetime
from smart_library.domain.entities.document import Document
from smart_library.domain.services.document_service import DocumentService

@pytest.fixture
def mock_repo():
    return Mock()

@pytest.fixture
def sample_document():
    return Document(
        id="doc-001",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        modified_at=datetime(2024, 1, 1, 12, 0, 0),
        parent_id=None,
        metadata={"source": "import"},
        type="research_article",
        source_path="/data/article.pdf",
        source_url="https://example.com/article.pdf",
        source_format="pdf",
        file_hash="abc123",
        version="v1",
        page_count=10,
        title="Sample Article",
        authors=["Alice", "Bob"],
        keywords=["AI", "ML"],
        doi="10.1234/example",
        publication_date="2024-01-01",
        publisher="Example Publisher",
        venue="Example Conference",
        year=2024,
        references=["ref1", "ref2"],
        citations=["cite1"]
    )

def test_add_document_calls_repo_add(mock_repo, sample_document):
    service = DocumentService(mock_repo)
    mock_repo.add.return_value = sample_document.id
    doc_id = service.add_document(sample_document)
    assert doc_id == sample_document.id
    mock_repo.add.assert_called_once_with(sample_document)

def test_get_document_calls_repo_get(mock_repo):
    service = DocumentService(mock_repo)
    mock_repo.get.return_value = "doc"
    result = service.get_document("doc-001")
    mock_repo.get.assert_called_once_with("doc-001")
    assert result == "doc"

def test_update_document_calls_repo_update(mock_repo, sample_document):
    service = DocumentService(mock_repo)
    service.update_document(sample_document)
    mock_repo.update.assert_called_once_with(sample_document)

def test_delete_document_calls_repo_delete(mock_repo):
    service = DocumentService(mock_repo)
    service.delete_document("doc-001")
    mock_repo.delete.assert_called_once_with("doc-001")

def test_update_document_metadata_updates_metadata_and_calls_update(mock_repo, sample_document):
    service = DocumentService(mock_repo)
    mock_repo.get.return_value = sample_document
    metadata = {"foo": "bar"}
    service.update_document_metadata(sample_document.id, metadata)
    assert sample_document.metadata["foo"] == "bar"
    mock_repo.update.assert_called_once_with(sample_document)