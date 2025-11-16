"""Unit tests for Entities dataclass."""

import json
import tempfile
from pathlib import Path

import pytest

from smart_library.dataclasses.entities import Entities, Entity
from smart_library.dataclasses.document import Document
from smart_library.dataclasses.page import Page


@pytest.fixture
def sample_entities_data():
    """Sample entities data for testing."""
    return [
        {
            "id": "doc-001",
            "type": "document",
            "data": {
                "page_count": 3,
                "title": "Neural Networks",
                "author": "John Doe"
            }
        },
        {
            "id": "doc-001_p0001",
            "type": "page",
            "data": {
                "page_number": 1,
                "page_text": "Introduction to neural networks. This is page 1."
            }
        },
        {
            "id": "doc-001_p0002",
            "type": "page",
            "data": {
                "page_number": 2,
                "page_text": "Deep learning architectures. This is page 2."
            }
        },
        {
            "id": "doc-001_p0003",
            "type": "page",
            "data": {
                "page_number": 3,
                "page_text": "Conclusion and future work. This is page 3."
            }
        },
        {
            "id": "text-001",
            "type": "text",
            "data": {
                "content": "Attention mechanisms allow models to focus on relevant parts."
            }
        },
        {
            "id": "term-001",
            "type": "term",
            "data": {
                "term": "backpropagation",
                "definition": "Algorithm for training neural networks"
            }
        }
    ]


@pytest.fixture
def sample_jsonl_file(tmp_path, sample_entities_data):
    """Create a temporary JSONL file with sample data."""
    jsonl_path = tmp_path / "test_entities.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for entry in sample_entities_data:
            f.write(json.dumps(entry) + "\n")
    return jsonl_path


@pytest.fixture
def entities(sample_entities_data):
    """Create Entities instance from sample data."""
    entities = Entities()
    for entry in sample_entities_data:
        entities.add(Entity(
            id=entry["id"],
            type=entry["type"],
            data=entry["data"]
        ))
    return entities


class TestEntity:
    """Tests for Entity dataclass."""
    
    def test_entity_creation(self):
        """Test creating a valid entity."""
        entity = Entity(
            id="test-001",
            type="document",
            data={"title": "Test"}
        )
        assert entity.id == "test-001"
        assert entity.type == "document"
        assert entity.data == {"title": "Test"}
    
    def test_entity_empty_id(self):
        """Test that empty id raises ValueError."""
        with pytest.raises(ValueError, match="id must be a non-empty string"):
            Entity(id="", type="document", data={})
    
    def test_entity_whitespace_id(self):
        """Test that whitespace-only id raises ValueError."""
        with pytest.raises(ValueError, match="id must be a non-empty string"):
            Entity(id="   ", type="document", data={})
    
    def test_entity_invalid_type(self):
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError, match="type must be one of"):
            Entity(id="test-001", type="invalid", data={})
    
    def test_entity_non_dict_data(self):
        """Test that non-dict data raises TypeError."""
        with pytest.raises(TypeError, match="data must be a dictionary"):
            Entity(id="test-001", type="document", data="not a dict")


class TestEntities:
    """Tests for Entities collection."""
    
    def test_empty_entities(self):
        """Test creating empty Entities collection."""
        entities = Entities()
        assert len(entities) == 0
        assert entities.entities == []
    
    def test_add_entity(self):
        """Test adding an entity."""
        entities = Entities()
        entity = Entity(id="test-001", type="document", data={})
        entities.add(entity)
        assert len(entities) == 1
        assert "test-001" in entities
    
    def test_add_duplicate_id(self):
        """Test that adding duplicate id raises ValueError."""
        entities = Entities()
        entity1 = Entity(id="test-001", type="document", data={})
        entity2 = Entity(id="test-001", type="page", data={})
        entities.add(entity1)
        with pytest.raises(ValueError, match="already exists"):
            entities.add(entity2)
    
    def test_get_entity(self, entities):
        """Test getting entity by id."""
        entity = entities.get("doc-001")
        assert entity is not None
        assert entity.id == "doc-001"
        assert entity.type == "document"
    
    def test_get_nonexistent_entity(self, entities):
        """Test getting non-existent entity returns None."""
        entity = entities.get("does-not-exist")
        assert entity is None
    
    def test_contains(self, entities):
        """Test __contains__ method."""
        assert "doc-001" in entities
        assert "text-001" in entities
        assert "does-not-exist" not in entities
    
    def test_len(self, entities):
        """Test __len__ method."""
        assert len(entities) == 6


class TestEntitiesTypeAccess:
    """Tests for typed access methods."""
    
    def test_get_by_type(self, entities):
        """Test getting entities by type."""
        pages = entities.get_by_type("page")
        assert len(pages) == 3
        assert all(e.type == "page" for e in pages)
        
        docs = entities.get_by_type("document")
        assert len(docs) == 1
        
        texts = entities.get_by_type("text")
        assert len(texts) == 1
        
        terms = entities.get_by_type("term")
        assert len(terms) == 1
    
    def test_get_document(self, entities):
        """Test getting document with pages loaded by reference."""
        doc = entities.get_document("doc-001")
        assert doc is not None
        assert isinstance(doc, Document)
        assert len(doc.pages) == 3
        
        # Check pages are loaded correctly
        assert doc.pages[0].page_number == 1
        assert "Introduction to neural networks" in doc.pages[0].page_text
        assert doc.pages[1].page_number == 2
        assert "Deep learning architectures" in doc.pages[1].page_text
        assert doc.pages[2].page_number == 3
        assert "Conclusion and future work" in doc.pages[2].page_text
    
    def test_get_document_nonexistent(self, entities):
        """Test getting non-existent document returns None."""
        doc = entities.get_document("does-not-exist")
        assert doc is None
    
    def test_get_document_wrong_type(self, entities):
        """Test getting document with page id returns None."""
        doc = entities.get_document("doc-001_p0001")
        assert doc is None
    
    def test_get_document_no_page_count(self):
        """Test getting document without page_count returns empty document."""
        entities = Entities()
        entities.add(Entity(
            id="doc-no-pages",
            type="document",
            data={"title": "No pages"}
        ))
        doc = entities.get_document("doc-no-pages")
        assert doc is not None
        assert len(doc.pages) == 0
    
    def test_get_document_missing_pages(self):
        """Test getting document with missing pages skips them."""
        entities = Entities()
        entities.add(Entity(
            id="doc-partial",
            type="document",
            data={"page_count": 3}
        ))
        entities.add(Entity(
            id="doc-partial_p0001",
            type="page",
            data={"page_number": 1, "page_text": "Page 1"}
        ))
        # Page 2 missing
        entities.add(Entity(
            id="doc-partial_p0003",
            type="page",
            data={"page_number": 3, "page_text": "Page 3"}
        ))
        
        doc = entities.get_document("doc-partial")
        assert doc is not None
        assert len(doc.pages) == 2
        assert doc.pages[0].page_number == 1
        assert doc.pages[1].page_number == 3
    
    def test_get_page(self, entities):
        """Test getting page by id."""
        page = entities.get_page("doc-001_p0001")
        assert page is not None
        assert isinstance(page, Page)
        assert page.page_number == 1
        assert "Introduction to neural networks" in page.page_text
    
    def test_get_page_nonexistent(self, entities):
        """Test getting non-existent page returns None."""
        page = entities.get_page("does-not-exist")
        assert page is None
    
    def test_get_page_wrong_type(self, entities):
        """Test getting page with document id returns None."""
        page = entities.get_page("doc-001")
        assert page is None
    
    def test_get_text(self, entities):
        """Test getting text content."""
        text = entities.get_text("text-001")
        assert text is not None
        assert "Attention mechanisms" in text
    
    def test_get_text_nonexistent(self, entities):
        """Test getting non-existent text returns None."""
        text = entities.get_text("does-not-exist")
        assert text is None
    
    def test_get_text_wrong_type(self, entities):
        """Test getting text with document id returns None."""
        text = entities.get_text("doc-001")
        assert text is None
    
    def test_get_term(self, entities):
        """Test getting term data."""
        term = entities.get_term("term-001")
        assert term is not None
        assert term["term"] == "backpropagation"
        assert "training neural networks" in term["definition"]
    
    def test_get_term_nonexistent(self, entities):
        """Test getting non-existent term returns None."""
        term = entities.get_term("does-not-exist")
        assert term is None
    
    def test_get_term_wrong_type(self, entities):
        """Test getting term with document id returns None."""
        term = entities.get_term("doc-001")
        assert term is None


class TestEntitiesIO:
    """Tests for load/write methods."""
    
    def test_load_from_jsonl(self, sample_jsonl_file):
        """Test loading entities from JSONL file."""
        entities = Entities.load(sample_jsonl_file)
        assert len(entities) == 6
        assert "doc-001" in entities
        assert "text-001" in entities
        assert "term-001" in entities
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            Entities.load("/does/not/exist.jsonl")
    
    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises ValueError."""
        bad_file = tmp_path / "bad.jsonl"
        with bad_file.open("w") as f:
            f.write("not valid json\n")
        
        with pytest.raises(ValueError, match="Invalid entity at line"):
            Entities.load(bad_file)
    
    def test_load_missing_required_fields(self, tmp_path):
        """Test loading entry without required fields raises ValueError."""
        bad_file = tmp_path / "bad.jsonl"
        with bad_file.open("w") as f:
            f.write('{"id": "test-001"}\n')  # Missing "type"
        
        with pytest.raises(ValueError, match="Invalid entity at line"):
            Entities.load(bad_file)
    
    def test_load_empty_lines(self, tmp_path):
        """Test loading file with empty lines skips them."""
        file_path = tmp_path / "with_empty.jsonl"
        with file_path.open("w") as f:
            f.write('{"id": "test-001", "type": "document", "data": {}}\n')
            f.write('\n')
            f.write('{"id": "test-002", "type": "page", "data": {"page_number": 1, "page_text": "test"}}\n')
            f.write('  \n')
        
        entities = Entities.load(file_path)
        assert len(entities) == 2
    
    def test_write_to_jsonl(self, entities, tmp_path):
        """Test writing entities to JSONL file."""
        output_path = tmp_path / "output.jsonl"
        entities.write(output_path)
        
        assert output_path.exists()
        
        # Load back and verify
        loaded = Entities.load(output_path)
        assert len(loaded) == len(entities)
        assert "doc-001" in loaded
        assert "text-001" in loaded
    
    def test_write_creates_parent_dirs(self, entities, tmp_path):
        """Test that write creates parent directories."""
        output_path = tmp_path / "subdir" / "nested" / "output.jsonl"
        entities.write(output_path)
        
        assert output_path.exists()
        assert output_path.parent.exists()
    
    def test_roundtrip(self, entities, tmp_path):
        """Test write then load preserves data."""
        output_path = tmp_path / "roundtrip.jsonl"
        entities.write(output_path)
        loaded = Entities.load(output_path)
        
        assert len(loaded) == len(entities)
        
        # Check document
        doc = loaded.get_document("doc-001")
        assert doc is not None
        assert len(doc.pages) == 3
        
        # Check text
        text = loaded.get_text("text-001")
        assert text is not None
        assert "Attention mechanisms" in text
        
        # Check term
        term = loaded.get_term("term-001")
        assert term is not None
        assert term["term"] == "backpropagation"


class TestEntitiesWithFixtures:
    """Tests using actual fixture files if they exist."""
    
    def test_load_fixture_if_exists(self):
        """Test loading from fixtures directory if file exists."""
        fixture_path = Path("/workspaces/smart-library/tests/fixtures/jsonl/entities.jsonl")
        if fixture_path.exists():
            entities = Entities.load(fixture_path)
            assert len(entities) > 0
            print(f"\nLoaded {len(entities)} entities from fixture")
            
            # Print summary
            for entity_type in ("document", "page", "text", "term"):
                count = len(entities.get_by_type(entity_type))
                print(f"  {entity_type}: {count}")
        else:
            pytest.skip("Fixture file not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])