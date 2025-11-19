import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from smart_library.domain.entities.document import Document
from smart_library.infrastructure.repositories.document_repository import DocumentRepository

@pytest.fixture
def mock_connection():
    conn = Mock()
    cursor = Mock()
    conn.execute = Mock(return_value=cursor)
    conn.commit = Mock()
    cursor.fetchone = Mock(return_value=None)
    return conn

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

class TestDocumentRepositoryAdd:
    def test_add_document_success(self, mock_connection, sample_document):
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = DocumentRepository()
            result = repo.add(sample_document)
            assert result == "doc-001"
            assert mock_connection.execute.called
            assert mock_connection.commit.called

class TestDocumentRepositoryGet:
    def test_get_document_success(self, mock_connection, sample_document):
        entity_row = {
            "id": "doc-001",
            "created_at": sample_document.created_at,
            "modified_at": sample_document.modified_at,
            "created_by": "system",
            "updated_by": "system",
            "parent_id": None,
            "metadata": '{"source": "import"}'
        }
        doc_row = {
            "id": "doc-001",
            "type": "research_article",
            "source_path": "/data/article.pdf",
            "source_url": "https://example.com/article.pdf",
            "source_format": "pdf",
            "file_hash": "abc123",
            "version": "v1",
            "page_count": 10,
            "title": "Sample Article",
            "authors": '["Alice", "Bob"]',
            "keywords": '["AI", "ML"]',
            "doi": "10.1234/example",
            "publication_date": "2024-01-01",
            "publisher": "Example Publisher",
            "venue": "Example Conference",
            "year": 2024,
            "references": '["ref1", "ref2"]',
            "citations": '["cite1"]'
        }
        entity_cursor = Mock()
        entity_cursor.fetchone = Mock(return_value=entity_row)
        doc_cursor = Mock()
        doc_cursor.fetchone = Mock(return_value=doc_row)
        mock_connection.execute = Mock(side_effect=[entity_cursor, doc_cursor])

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = DocumentRepository()
            result = repo.get("doc-001")
            assert result is not None
            assert result.id == "doc-001"
            assert result.title == "Sample Article"
            assert result.authors == ["Alice", "Bob"]
            assert result.keywords == ["AI", "ML"]
            assert result.references == ["ref1", "ref2"]
            assert result.citations == ["cite1"]

    def test_get_document_not_found(self, mock_connection):
        cursor = Mock()
        cursor.fetchone = Mock(return_value=None)
        mock_connection.execute = Mock(return_value=cursor)
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = DocumentRepository()
            result = repo.get("nonexistent")
            assert result is None

class TestDocumentRepositoryUpdate:
    def test_update_document_success(self, mock_connection, sample_document):
        sample_document.title = "Updated Title"
        sample_document.keywords.append("updated")
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = DocumentRepository()
            repo.update(sample_document)
            assert mock_connection.execute.called
            assert mock_connection.commit.called

class TestDocumentRepositoryDelete:
    def test_delete_document_success(self, mock_connection):
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = DocumentRepository()
            repo.delete("doc-001")
            assert mock_connection.execute.called
            assert mock_connection.commit.called

if __name__ == "__main__":
    pytest.main([__file__, "-v"])