import pytest
from unittest.mock import Mock
from datetime import datetime
from smart_library.domain.entities.term import Term
from smart_library.domain.services.term_service import TermService

@pytest.fixture
def mock_repo():
    return Mock()

@pytest.fixture
def sample_term():
    return Term(
        id="term-001",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        modified_at=datetime(2024, 1, 1, 12, 0, 0),
        canonical_name="AI",
        aliases=["artificial intelligence"],
        related_terms=["ML"],
        sense="technology",
        metadata={"source": "import"}
    )

def test_add_term_calls_repo_add(mock_repo, sample_term):
    service = TermService(mock_repo)
    mock_repo.add.return_value = sample_term.id
    term_id = service.add_term(sample_term)
    assert term_id == sample_term.id
    mock_repo.add.assert_called_once_with(sample_term)

def test_get_term_calls_repo_get(mock_repo):
    service = TermService(mock_repo)
    service.get_term("term-001")
    mock_repo.get.assert_called_once_with("term-001")

def test_update_term_calls_repo_update(mock_repo, sample_term):
    service = TermService(mock_repo)
    service.update_term(sample_term)
    mock_repo.update.assert_called_once_with(sample_term)

def test_delete_term_calls_repo_delete(mock_repo):
    service = TermService(mock_repo)
    service.delete_term("term-001")
    mock_repo.delete.assert_called_once_with("term-001")

def test_update_term_metadata_updates_metadata_and_calls_update(mock_repo, sample_term):
    service = TermService(mock_repo)
    mock_repo.get.return_value = sample_term
    metadata = {"foo": "bar"}
    service.update_term_metadata(sample_term.id, metadata)
    assert sample_term.metadata["foo"] == "bar"
    mock_repo.update.assert_called_once_with(sample_term)