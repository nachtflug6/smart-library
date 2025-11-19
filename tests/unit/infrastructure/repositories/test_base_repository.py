import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from smart_library.infrastructure.repositories.base_repository import (
    BaseRepository,
    _to_json,
    _from_json
)
from smart_library.domain.entities.entity import Entity


class TestHelperFunctions:
    """Tests for JSON helper functions."""

    def test_to_json_with_none(self):
        """Test _to_json with None value."""
        assert _to_json(None) is None

    def test_to_json_with_dict(self):
        """Test _to_json with dictionary."""
        data = {"key": "value", "num": 42}
        result = _to_json(data)
        assert result == '{"key": "value", "num": 42}'

    def test_to_json_with_list(self):
        """Test _to_json with list."""
        data = ["a", "b", "c"]
        result = _to_json(data)
        assert result == '["a", "b", "c"]'

    def test_from_json_with_empty_string(self):
        """Test _from_json with empty string."""
        assert _from_json("", []) == []
        assert _from_json("", {}) == {}

    def test_from_json_with_none(self):
        """Test _from_json with None."""
        assert _from_json(None, []) == []

    def test_from_json_with_valid_json(self):
        """Test _from_json with valid JSON string."""
        json_str = '{"key": "value"}'
        result = _from_json(json_str, {})
        assert result == {"key": "value"}

    def test_from_json_with_invalid_json(self):
        """Test _from_json with invalid JSON returns default."""
        result = _from_json("{invalid}", {"default": True})
        assert result == {"default": True}


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
def mock_entity():
    """Create a mock entity."""
    return Entity(
        id="test-001",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        modified_at=datetime(2024, 1, 1, 12, 0, 0),
        created_by="user1",
        updated_by="user1",
        parent_id="parent-001",
        metadata={"test": "data"}
    )


class TestBaseRepository:
    """Tests for BaseRepository base class."""

    def test_init_gets_connection(self):
        """Test repository initialization gets connection."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_get_conn.return_value = mock_conn
            
            repo = BaseRepository()
            
            assert repo.conn == mock_conn
            mock_get_conn.assert_called_once()

    def test_insert_entity(self, mock_connection, mock_entity):
        """Test _insert_entity inserts into entity table."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = BaseRepository()
            repo._insert_entity(mock_entity)

            mock_connection.execute.assert_called_once()
            call_args = mock_connection.execute.call_args[0]
            
            assert "INSERT INTO entity" in call_args[0]
            assert call_args[1][0] == "test-001"
            assert call_args[1][1] == datetime(2024, 1, 1, 12, 0, 0)
            assert call_args[1][6] == "Entity"
            assert json.loads(call_args[1][7]) == {"test": "data"}

    def test_insert_entity_with_none_parent_id(self, mock_connection):
        """Test _insert_entity with None parent_id."""
        entity = Entity(
            id="test-002",
            parent_id=None,
            metadata={}
        )
        
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = BaseRepository()
            repo._insert_entity(entity)

            call_args = mock_connection.execute.call_args[0]
            assert call_args[1][5] is None

    def test_update_entity_meta(self, mock_connection, mock_entity):
        """Test _update_entity_meta updates entity metadata."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = BaseRepository()
            mock_entity.metadata = {"updated": "metadata"}
            
            repo._update_entity_meta(mock_entity)

            mock_connection.execute.assert_called_once()
            call_args = mock_connection.execute.call_args[0]
            
            assert "UPDATE entity" in call_args[0]
            assert call_args[1][3] == "test-001"
            assert json.loads(call_args[1][2]) == {"updated": "metadata"}

    def test_delete_entity(self, mock_connection):
        """Test _delete_entity deletes from entity table."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = BaseRepository()
            repo._delete_entity("test-001")

            mock_connection.execute.assert_called_once()
            call_args = mock_connection.execute.call_args[0]
            
            assert "DELETE FROM entity" in call_args[0]
            assert call_args[1] == ("test-001",)

    def test_fetch_entity_row_found(self, mock_connection):
        """Test _fetch_entity_row returns entity data."""
        entity_data = {
            "id": "test-001",
            "created_at": datetime.now(),
            "metadata": '{"test": "data"}'
        }
        
        cursor = Mock()
        cursor.fetchone = Mock(return_value=entity_data)
        mock_connection.execute = Mock(return_value=cursor)
        
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = BaseRepository()
            result = repo._fetch_entity_row("test-001")

            assert result == entity_data
            mock_connection.execute.assert_called_once()
            call_args = mock_connection.execute.call_args[0]
            assert "SELECT * FROM entity" in call_args[0]

    def test_fetch_entity_row_not_found(self, mock_connection):
        """Test _fetch_entity_row returns None when not found."""
        cursor = Mock()
        cursor.fetchone = Mock(return_value=None)
        mock_connection.execute = Mock(return_value=cursor)
        
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = BaseRepository()
            result = repo._fetch_entity_row("nonexistent")

            assert result is None

    def test_row_to_dict_with_row(self):
        """Test _row_to_dict converts row to dict."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection'):
            repo = BaseRepository()
            row = {"id": "test", "name": "Test"}
            result = repo._row_to_dict(row)
            
            assert result == {"id": "test", "name": "Test"}

    def test_row_to_dict_with_none(self):
        """Test _row_to_dict with None returns empty dict."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection'):
            repo = BaseRepository()
            result = repo._row_to_dict(None)
            
            assert result == {}


class ConcreteRepository(BaseRepository):
    """Concrete repository for testing base class methods."""
    table = "test_table"
    columns = {
        "id": "id",
        "name": "name",
        "tags": "tags"
    }
    json_columns = {"tags"}


class TestBaseRepositoryGenericOps:
    """Tests for generic CRUD operations in BaseRepository."""

    def test_add_entity(self, mock_connection, mock_entity):
        """Test add method inserts entity and child record."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = ConcreteRepository()
            mock_entity.name = "Test Name"
            mock_entity.tags = ["tag1", "tag2"]
            
            result = repo.add(mock_entity)

            assert result == "test-001"
            assert mock_connection.execute.call_count == 2
            assert mock_connection.commit.called

    def test_get_with_join(self, mock_connection):
        """Test get method with join_entity=True."""
        row_data = {
            "id": "test-001",
            "name": "Test",
            "created_at": datetime.now(),
            "metadata": "{}"
        }
        
        cursor = Mock()
        cursor.fetchone = Mock(return_value=row_data)
        mock_connection.execute = Mock(return_value=cursor)
        
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = ConcreteRepository()
            repo.join_entity = True
            
            result = repo.get("test-001")

            assert result == row_data
            call_args = mock_connection.execute.call_args[0]
            assert "JOIN" in call_args[0]

    def test_get_without_join(self, mock_connection):
        """Test get method with join_entity=False."""
        row_data = {"id": "test-001", "name": "Test"}
        
        cursor = Mock()
        cursor.fetchone = Mock(return_value=row_data)
        mock_connection.execute = Mock(return_value=cursor)
        
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = ConcreteRepository()
            repo.join_entity = False
            
            result = repo.get("test-001")

            assert result == row_data
            call_args = mock_connection.execute.call_args[0]
            assert "JOIN" not in call_args[0]

    def test_get_not_found(self, mock_connection):
        """Test get method returns None when not found."""
        cursor = Mock()
        cursor.fetchone = Mock(return_value=None)
        mock_connection.execute = Mock(return_value=cursor)
        
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = ConcreteRepository()
            result = repo.get("nonexistent")

            assert result is None

    def test_delete(self, mock_connection):
        """Test delete method removes entity."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = ConcreteRepository()
            repo.delete("test-001")

            mock_connection.execute.assert_called_once()
            assert mock_connection.commit.called
            
            call_args = mock_connection.execute.call_args[0]
            assert "DELETE FROM entity" in call_args[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])