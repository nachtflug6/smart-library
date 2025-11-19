import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from smart_library.domain.entities.text import Text
from smart_library.infrastructure.repositories.text_repository import TextRepository


@pytest.fixture
def mock_connection():
    """Mock database connection."""
    conn = Mock()
    cursor = Mock()
    conn.execute = Mock(return_value=cursor)
    conn.commit = Mock()
    cursor.fetchone = Mock(return_value=None)
    return conn


@pytest.fixture
def sample_text():
    """Create sample Text entity."""
    return Text(
        id="text-001",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        modified_at=datetime(2024, 1, 1, 12, 0, 0),
        parent_id="page-001",
        metadata={"source": "extraction"},
        content="Sample text content from page",
        text_type="paragraph",
        index=1
    )


class TestTextRepositoryAdd:
    """Tests for TextRepository.add() method."""

    def test_add_text_success(self, mock_connection, sample_text):
        """Test successfully adding a text entity."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TextRepository()
            result = repo.add(sample_text)

            assert result == "text-001"
            assert mock_connection.execute.call_count == 2
            assert mock_connection.commit.called

    def test_add_text_without_parent_id_raises_error(self, mock_connection):
        """Test adding text without parent_id raises ValueError."""
        text = Text(
            id="text-002",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
            content="Test content",
            text_type="paragraph"
        )

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TextRepository()
            
            with pytest.raises(ValueError, match="Text.parent_id should reference Page or Document id"):
                repo.add(text)

    def test_add_text_with_various_types(self, mock_connection):
        """Test adding text with different type values."""
        types = ["paragraph", "heading", "caption", "summary", "chunk"]
        
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TextRepository()
            
            for text_type in types:
                text = Text(
                    id=f"text-{text_type}",
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    parent_id="page-001",
                    content=f"Content of type {text_type}",
                    text_type=text_type
                )
                result = repo.add(text)
                assert result == f"text-{text_type}"


class TestTextRepositoryGet:
    """Tests for TextRepository.get() method."""

    def test_get_text_success(self, mock_connection):
        """Test successfully retrieving a text entity."""
        entity_row = {
            "id": "text-001",
            "created_at": datetime(2024, 1, 1),
            "modified_at": datetime(2024, 1, 1),
            "created_by": "system",
            "updated_by": "system",
            "parent_id": "page-001",
            "metadata": '{"source": "extraction"}'
        }

        text_row = {
            "id": "text-001",
            "type": "paragraph",
            "index": 1,
            "content": "Sample text content"
        }

        entity_cursor = Mock()
        entity_cursor.fetchone = Mock(return_value=entity_row)
        
        text_cursor = Mock()
        text_cursor.fetchone = Mock(return_value=text_row)

        mock_connection.execute = Mock(side_effect=[entity_cursor, text_cursor])

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TextRepository()
            result = repo.get("text-001")

            assert result is not None
            assert result.id == "text-001"
            assert result.content == "Sample text content"
            assert result.text_type == "paragraph"
            assert result.index == 1
            assert result.parent_id == "page-001"

    def test_get_text_not_found(self, mock_connection):
        """Test getting text when entity doesn't exist."""
        cursor = Mock()
        cursor.fetchone = Mock(return_value=None)
        mock_connection.execute = Mock(return_value=cursor)

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TextRepository()
            result = repo.get("nonexistent")

            assert result is None

    def test_get_text_with_null_optional_fields(self, mock_connection):
        """Test getting text with null optional fields."""
        entity_row = {
            "id": "text-min",
            "created_at": datetime.now(),
            "modified_at": datetime.now(),
            "parent_id": "page-001",
            "metadata": None
        }

        text_row = {
            "id": "text-min",
            "type": None,
            "index": None,
            "content": "Minimal content"
        }

        entity_cursor = Mock()
        entity_cursor.fetchone = Mock(return_value=entity_row)
        
        text_cursor = Mock()
        text_cursor.fetchone = Mock(return_value=text_row)

        mock_connection.execute = Mock(side_effect=[entity_cursor, text_cursor])

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TextRepository()
            result = repo.get("text-min")

            assert result is not None
            assert result.content == "Minimal content"
            assert result.text_type is None
            assert result.index is None


class TestTextRepositoryUpdate:
    """Tests for TextRepository.update() method."""

    def test_update_text_success(self, mock_connection, sample_text):
        """Test successfully updating a text entity."""
        sample_text.content = "Updated content"
        sample_text.text_type = "heading"
        sample_text.index = 2

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TextRepository()
            repo.update(sample_text)

            assert mock_connection.execute.call_count == 2
            assert mock_connection.commit.called

    def test_update_text_change_type(self, mock_connection):
        """Test updating text type field."""
        text = Text(
            id="text-001",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id="page-001",
            content="Content",
            text_type="paragraph",
            index=1
        )

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TextRepository()
            text.text_type = "summary"
            repo.update(text)

            calls = mock_connection.execute.call_args_list
            text_update = calls[1]
            assert "UPDATE text_entity" in text_update[0][0]


class TestTextRepositoryDelete:
    """Tests for TextRepository.delete() method."""

    def test_delete_text_success(self, mock_connection):
        """Test successfully deleting a text entity."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TextRepository()
            repo.delete("text-001")

            assert mock_connection.execute.called
            assert mock_connection.commit.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])