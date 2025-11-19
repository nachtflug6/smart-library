import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from smart_library.domain.entities.term import Term
from smart_library.infrastructure.repositories.term_repository import TermRepository


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
def sample_term():
    """Create sample Term entity."""
    return Term(
        id="term-001",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        modified_at=datetime(2024, 1, 1, 12, 0, 0),
        metadata={"confidence": 0.95},
        canonical_name="neural network",
        sense="algorithm",
        definition="A computational model inspired by biological neural networks",
        aliases=["NN", "artificial neural network", "ANN"],
        domain="machine learning",
        related_terms=["deep learning", "perceptron", "backpropagation"]
    )

@pytest.fixture(autouse=True)
def patch_db_connection(monkeypatch, mock_connection):
    """Automatically patch get_connection to return mock_connection for all tests."""
    monkeypatch.setattr(
        "smart_library.infrastructure.db.db.get_connection",
        lambda *args, **kwargs: mock_connection
    )

class TestTermRepositoryAdd:
    def test_add_term_success(self, mock_connection, sample_term):
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            result = repo.add(sample_term)
            assert result == "term-001"
            assert mock_connection.execute.call_count == 2
            assert mock_connection.commit.called

    def test_add_term_with_minimal_fields(self, mock_connection):
        term = Term(
            id="term-minimal",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            canonical_name="AI"
        )
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            result = repo.add(term)
            assert result == "term-minimal"
            assert mock_connection.commit.called

    def test_add_term_json_encoding(self, mock_connection):
        term = Term(
            id="term-json",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            canonical_name="machine learning",
            aliases=["ML", "statistical learning"],
            related_terms=["AI", "deep learning"]
        )
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            repo.add(term)
            calls = mock_connection.execute.call_args_list
            term_insert = calls[1]
            assert "INSERT INTO term" in term_insert[0][0]


class TestTermRepositoryGet:
    """Tests for TermRepository.get() method."""

    def test_get_term_success(self, mock_connection):
        """Test successfully retrieving a term."""
        entity_row = {
            "id": "term-001",
            "created_at": datetime(2024, 1, 1),
            "modified_at": datetime(2024, 1, 1),
            "created_by": "system",
            "updated_by": "system",
            "parent_id": None,
            "metadata": '{"confidence": 0.95}'
        }

        term_row = {
            "id": "term-001",
            "canonical_name": "neural network",
            "sense": "algorithm",
            "definition": "A computational model",
            "aliases": '["NN", "ANN"]',
            "domain": "machine learning",
            "related_terms": '["deep learning", "perceptron"]'
        }

        entity_cursor = Mock()
        entity_cursor.fetchone = Mock(return_value=entity_row)
        
        term_cursor = Mock()
        term_cursor.fetchone = Mock(return_value=term_row)

        mock_connection.execute = Mock(side_effect=[entity_cursor, term_cursor])

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            result = repo.get("term-001")

            assert result is not None
            assert result.id == "term-001"
            assert result.canonical_name == "neural network"
            assert result.sense == "algorithm"
            assert result.aliases == ["NN", "ANN"]
            assert result.related_terms == ["deep learning", "perceptron"]
            assert result.domain == "machine learning"

    def test_get_term_not_found(self, mock_connection):
        """Test getting term when entity doesn't exist."""
        cursor = Mock()
        cursor.fetchone = Mock(return_value=None)
        mock_connection.execute = Mock(return_value=cursor)

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            result = repo.get("nonexistent")

            assert result is None

    def test_get_term_with_empty_json_fields(self, mock_connection):
        """Test getting term with empty/null JSON fields."""
        entity_row = {
            "id": "term-empty",
            "created_at": datetime.now(),
            "modified_at": datetime.now(),
            "parent_id": None,
            "metadata": None
        }

        term_row = {
            "id": "term-empty",
            "canonical_name": "term",
            "sense": None,
            "definition": None,
            "aliases": None,
            "domain": None,
            "related_terms": ""
        }

        entity_cursor = Mock()
        entity_cursor.fetchone = Mock(return_value=entity_row)
        
        term_cursor = Mock()
        term_cursor.fetchone = Mock(return_value=term_row)

        mock_connection.execute = Mock(side_effect=[entity_cursor, term_cursor])

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            result = repo.get("term-empty")

            assert result is not None
            assert result.canonical_name == "term"
            assert result.aliases == []
            assert result.related_terms == []


class TestTermRepositoryUpdate:
    """Tests for TermRepository.update() method."""

    def test_update_term_success(self, mock_connection, sample_term):
        """Test successfully updating a term."""
        sample_term.definition = "Updated definition"
        sample_term.aliases.append("new alias")

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            repo.update(sample_term)

            assert mock_connection.execute.call_count == 2
            assert mock_connection.commit.called

    def test_update_term_change_sense(self, mock_connection):
        """Test updating term sense (disambiguation)."""
        term = Term(
            id="term-001",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            canonical_name="Kalman",
            sense="person"
        )

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            term.sense = "algorithm"
            repo.update(term)

            calls = mock_connection.execute.call_args_list
            term_update = calls[1]
            assert "UPDATE term" in term_update[0][0]

    def test_update_term_add_related_terms(self, mock_connection):
        """Test updating term with new related terms."""
        term = Term(
            id="term-001",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            canonical_name="AI",
            related_terms=["ML"]
        )

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            term.related_terms.extend(["deep learning", "NLP"])
            repo.update(term)

            assert mock_connection.commit.called


class TestTermRepositoryDelete:
    """Tests for TermRepository.delete() method."""

    def test_delete_term_success(self, mock_connection):
        """Test successfully deleting a term."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            repo.delete("term-001")

            assert mock_connection.execute.called
            assert mock_connection.commit.called

    def test_delete_nonexistent_term(self, mock_connection):
        """Test deleting non-existent term doesn't raise error."""
        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            repo.delete("nonexistent")

            assert mock_connection.execute.called


class TestTermRepositoryIntegration:
    """Integration-style tests for TermRepository."""

    def test_add_and_get_term(self, mock_connection):
        """Test adding then retrieving a term."""
        term = Term(
            id="term-integration",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            canonical_name="transformer",
            sense="architecture",
            aliases=["attention mechanism"],
            domain="NLP"
        )

        with patch('smart_library.infrastructure.repositories.base_repository.get_connection', return_value=mock_connection):
            repo = TermRepository()
            repo.add(term)

            # Setup mock for get
            entity_row = {
                "id": "term-integration",
                "created_at": term.created_at,
                "modified_at": term.modified_at,
                "parent_id": None,
                "metadata": "{}"
            }

            term_row = {
                "id": "term-integration",
                "canonical_name": "transformer",
                "sense": "architecture",
                "definition": None,
                "aliases": '["attention mechanism"]',
                "domain": "NLP",
                "related_terms": "[]"
            }

            entity_cursor = Mock()
            entity_cursor.fetchone = Mock(return_value=entity_row)
            
            term_cursor = Mock()
            term_cursor.fetchone = Mock(return_value=term_row)

            mock_connection.execute = Mock(side_effect=[entity_cursor, term_cursor])

            result = repo.get("term-integration")

            assert result is not None
            assert result.canonical_name == "transformer"
            assert result.aliases == ["attention mechanism"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])