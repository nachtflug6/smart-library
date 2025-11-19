import pytest
from unittest.mock import Mock
from datetime import datetime
from smart_library.domain.entities.text import Text
from smart_library.application.services.text_service import TextService

@pytest.fixture
def mock_text_repo():
    return Mock()

@pytest.fixture
def mock_entity_repo():
    repo = Mock()
    repo.get.return_value = True
    return repo

@pytest.fixture
def mock_embedding_service():
    svc = Mock()
    svc.embed.return_value = [0.1, 0.2, 0.3]
    return svc

@pytest.fixture
def sample_text():
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

def test_add_text_success(mock_text_repo, mock_entity_repo, sample_text):
    service = TextService(mock_text_repo, mock_entity_repo)
    mock_text_repo.add.return_value = sample_text.id
    text_id = service.add_text(sample_text)
    assert text_id == sample_text.id
    mock_text_repo.add.assert_called_once_with(sample_text)

def test_add_text_missing_parent_raises(mock_text_repo, mock_entity_repo, sample_text):
    service = TextService(mock_text_repo, mock_entity_repo)
    sample_text.parent_id = None
    with pytest.raises(ValueError):
        service.add_text(sample_text)

def test_add_text_parent_not_found_raises(mock_text_repo, sample_text):
    entity_repo = Mock()
    entity_repo.get.return_value = None
    service = TextService(mock_text_repo, entity_repo)
    with pytest.raises(ValueError):
        service.add_text(sample_text)

def test_add_text_with_embedding(mock_text_repo, mock_entity_repo, mock_embedding_service, sample_text):
    service = TextService(mock_text_repo, mock_entity_repo, mock_embedding_service)
    mock_text_repo.add.return_value = sample_text.id
    text_id = service.add_text(sample_text)
    assert "embedding" in sample_text.metadata
    mock_embedding_service.embed.assert_called_once_with(sample_text.content)
    mock_text_repo.add.assert_called_once_with(sample_text)

def test_update_text_calls_repo_update(mock_text_repo, sample_text):
    service = TextService(mock_text_repo, Mock())
    service.update_text(sample_text)
    mock_text_repo.update.assert_called_once_with(sample_text)

def test_delete_text_calls_repo_delete(mock_text_repo):
    service = TextService(mock_text_repo, Mock())
    service.delete_text("text-001")
    mock_text_repo.delete.assert_called_once_with("text-001")