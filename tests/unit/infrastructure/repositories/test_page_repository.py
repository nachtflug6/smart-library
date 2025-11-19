import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from smart_library.domain.entities.page import Page
from smart_library.infrastructure.repositories.page_repository import PageRepository

@pytest.fixture
def mock_connection():
    conn = Mock()
    cursor = Mock()
    cursor.fetchone = Mock(return_value=None)
    conn.execute = Mock(return_value=cursor)
    conn.commit = Mock()
    return conn

@pytest.fixture
def sample_page():
    return Page(
        id="page-001",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        modified_at=datetime(2024, 1, 1, 12, 0, 0),
        parent_id="doc-001",
        metadata={"source": "import"},
        page_number=1,
        document_id="doc-001",
        full_text="Sample page text",
        token_count=100,
        paragraphs=["para1", "para2"],
        sections=["sec1"],
        is_reference_page=True,
        is_title_page=False,
        has_tables=True,
        has_figures=False,
        has_equations=None
    )

class TestPageRepositoryAdd:
    def test_add_page_success(self, sample_page, mock_connection):
        with patch("smart_library.infrastructure.repositories.base_repository.get_connection", return_value=mock_connection):
            repo = PageRepository()
            result = repo.add(sample_page)
            assert result == "page-001"
            assert repo.conn.execute.called
            assert repo.conn.commit.called

    def test_add_page_without_parent_id_raises_error(self, mock_connection):
        with patch("smart_library.infrastructure.repositories.base_repository.get_connection", return_value=mock_connection):
            page = Page(
                id="page-002",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                parent_id=None,
                page_number=2
            )
            repo = PageRepository()
            with pytest.raises(ValueError, match="Page.parent_id must reference a Document.id"):
                repo.add(page)

class TestPageRepositoryGet:
    def test_get_page_success(self, sample_page, mock_connection):
        entity_row = {
            "id": "page-001",
            "created_at": sample_page.created_at,
            "modified_at": sample_page.modified_at,
            "created_by": "system",
            "updated_by": "system",
            "parent_id": "doc-001",
            "metadata": '{"source": "import"}'
        }
        page_row = {
            "id": "page-001",
            "page_number": 1,
            "full_text": "Sample page text",
            "token_count": 100,
            "paragraphs": '["para1", "para2"]',
            "sections": '["sec1"]',
            "is_reference_page": 1,
            "is_title_page": 0,
            "has_tables": 1,
            "has_figures": 0,
            "has_equations": None
        }
        entity_cursor = Mock()
        entity_cursor.fetchone = Mock(return_value=entity_row)
        page_cursor = Mock()
        page_cursor.fetchone = Mock(return_value=page_row)
        mock_connection.execute.side_effect = [entity_cursor, page_cursor]
        with patch("smart_library.infrastructure.repositories.base_repository.get_connection", return_value=mock_connection):
            repo = PageRepository()
            result = repo.get("page-001")
            assert result is not None
            assert result.id == "page-001"
            assert result.page_number == 1
            assert result.full_text == "Sample page text"
            assert result.paragraphs == ["para1", "para2"]
            assert result.sections == ["sec1"]
            assert result.is_reference_page is True
            assert result.is_title_page is False
            assert result.has_tables is True
            assert result.has_figures is False
            assert result.has_equations is None

    def test_get_page_not_found(self, mock_connection):
        cursor = Mock()
        cursor.fetchone = Mock(return_value=None)
        mock_connection.execute.return_value = cursor
        with patch("smart_library.infrastructure.repositories.base_repository.get_connection", return_value=mock_connection):
            repo = PageRepository()
            result = repo.get("nonexistent")
            assert result is None

class TestPageRepositoryUpdate:
    def test_update_page_success(self, sample_page, mock_connection):
        with patch("smart_library.infrastructure.repositories.base_repository.get_connection", return_value=mock_connection):
            sample_page.full_text = "Updated text"
            sample_page.token_count = 200
            sample_page.is_title_page = True
            repo = PageRepository()
            repo.update(sample_page)
            assert repo.conn.execute.called
            assert repo.conn.commit.called

class TestPageRepositoryDelete:
    def test_delete_page_success(self, mock_connection):
        with patch("smart_library.infrastructure.repositories.base_repository.get_connection", return_value=mock_connection):
            repo = PageRepository()
            repo.delete("page-001")
            assert repo.conn.execute.called
            assert repo.conn.commit.called

if __name__ == "__main__":
    pytest.main([__file__, "-v"])