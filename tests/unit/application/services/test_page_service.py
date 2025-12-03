import pytest
from unittest.mock import Mock
from datetime import datetime
from smart_library.domain.entities.page import Page
from smart_library.domain.services.page_service import PageService

@pytest.fixture
def mock_page_repo():
    return Mock()

@pytest.fixture
def mock_entity_repo():
    repo = Mock()
    repo.get.return_value = True
    return repo

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

def test_add_page_success(mock_page_repo, mock_entity_repo, sample_page):
    service = PageService(mock_page_repo, mock_entity_repo)
    mock_page_repo.add.return_value = sample_page.id
    page_id = service.add_page(sample_page)
    assert page_id == sample_page.id
    mock_page_repo.add.assert_called_once_with(sample_page)

def test_add_page_missing_parent_raises(mock_page_repo, mock_entity_repo, sample_page):
    service = PageService(mock_page_repo, mock_entity_repo)
    sample_page.parent_id = None
    with pytest.raises(ValueError):
        service.add_page(sample_page)

def test_get_page_calls_repo_get(mock_page_repo):
    service = PageService(mock_page_repo)
    service.get_page("page-001")
    mock_page_repo.get.assert_called_once_with("page-001")

def test_update_page_calls_repo_update(mock_page_repo, sample_page):
    service = PageService(mock_page_repo)
    service.update_page(sample_page)
    mock_page_repo.update.assert_called_once_with(sample_page)

def test_delete_page_calls_repo_delete(mock_page_repo):
    service = PageService(mock_page_repo)
    service.delete_page("page-001")
    mock_page_repo.delete.assert_called_once_with("page-001")