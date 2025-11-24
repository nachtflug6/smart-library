import pytest
from unittest.mock import Mock, patch
from smart_library.infrastructure.repositories.relationship_repository import RelationshipRepository

@pytest.fixture
def mock_conn():
    return Mock()

@pytest.fixture
def repo(mock_conn):
    with patch("smart_library.infrastructure.repositories.base_repository.get_connection", return_value=mock_conn):
        return RelationshipRepository()

def test_add_relationship(repo, mock_conn):
    repo.conn = mock_conn
    mock_conn.execute.return_value = None
    mock_conn.commit.return_value = None
    result = repo.add("rel-1", "src-1", "tgt-1", "cites", {"foo": "bar"})
    assert result == "rel-1"
    mock_conn.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

def test_get_relationship(repo, mock_conn):
    repo.conn = mock_conn
    mock_row = {
        "id": "rel-1",
        "source_id": "src-1",
        "target_id": "tgt-1",
        "type": "cites",
        "metadata": "{\"foo\": \"bar\"}"
    }
    mock_conn.execute.return_value.fetchone.return_value = mock_row
    result = repo.get("rel-1")
    assert result["id"] == "rel-1"
    assert result["source_id"] == "src-1"
    assert result["target_id"] == "tgt-1"
    assert result["type"] == "cites"
    assert isinstance(result["metadata"], dict)

def test_get_relationship_not_found(repo, mock_conn):
    repo.conn = mock_conn
    mock_conn.execute.return_value.fetchone.return_value = None
    result = repo.get("notfound")
    assert result is None

def test_delete_relationship(repo, mock_conn):
    repo.conn = mock_conn
    mock_conn.execute.return_value = None
    mock_conn.commit.return_value = None
    repo.delete("rel-1")
    mock_conn.execute.assert_called_once()
    mock_conn.commit.assert_called_once()