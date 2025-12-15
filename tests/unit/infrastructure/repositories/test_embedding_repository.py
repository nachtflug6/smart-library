import pytest
from unittest.mock import Mock, patch
from smart_library.infrastructure.repositories.vector_repository import EmbeddingRepository

@pytest.fixture
def mock_conn():
    return Mock()

@pytest.fixture
def repo(mock_conn):
    with patch("smart_library.infrastructure.repositories.base_repository.get_connection", return_value=mock_conn):
        return EmbeddingRepository()

def test_add_embedding(repo, mock_conn):
    repo.conn = mock_conn
    mock_conn.execute.return_value = None
    mock_conn.commit.return_value = None
    result = repo.add("emb-1", [0.1, 0.2], "entity-1", "test-model", {"foo": "bar"})
    assert result == "emb-1"
    mock_conn.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

def test_get_embedding(repo, mock_conn):
    repo.conn = mock_conn
    mock_row = {
        "id": "emb-1",
        "vector": "[0.1, 0.2]",
        "entity_id": "entity-1",
        "model": "test-model",
        "metadata": "{\"foo\": \"bar\"}"
    }
    mock_conn.execute.return_value.fetchone.return_value = mock_row
    result = repo.get("emb-1")
    assert result["id"] == "emb-1"
    assert isinstance(result["vector"], list)
    assert result["entity_id"] == "entity-1"
    assert result["model"] == "test-model"
    assert isinstance(result["metadata"], dict)

def test_get_embedding_not_found(repo, mock_conn):
    repo.conn = mock_conn
    mock_conn.execute.return_value.fetchone.return_value = None
    result = repo.get("notfound")
    assert result is None

def test_delete_embedding(repo, mock_conn):
    repo.conn = mock_conn
    mock_conn.execute.return_value = None
    mock_conn.commit.return_value = None
    repo.delete("emb-1")
    mock_conn.execute.assert_called_once()
    mock_conn.commit.assert_called_once()