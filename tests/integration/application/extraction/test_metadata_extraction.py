import pytest
from smart_library.domain.entities.document import Document
from smart_library.domain.entities.page import Page
from smart_library.application.pipelines.metadata_extraction import SimpleMetadataExtractor
from smart_library.config import OllamaConfig

class RealDocumentService:
    @staticmethod
    def default_instance():
        return RealDocumentService()
    def get_pages(self, doc_id):
        # Use a real test page from the integration data folder
        with open("/workspaces/smart-library/tests/integration/data/Ma2022/p01.txt", "r") as f:
            page_text = f.read()
        return [Page(
            page_number=1,
            document_id=doc_id,
            full_text=page_text
        )]

@pytest.mark.integration
def test_metadata_extraction_with_ollama():
    # Arrange
    doc = Document(
        id="Ma2022",
        title=None,
        authors=None,
        abstract=None
    )
    extractor = SimpleMetadataExtractor(
        ollama_url=OllamaConfig.GENERATE_URL,
        ollama_model=OllamaConfig.GENERATION_MODEL,
        document_service=RealDocumentService()
    )

    # Act
    updated_doc = extractor.extract(doc)

    # Assert
    print("Extracted Title:", updated_doc.title)
    print("Extracted Authors:", updated_doc.authors)
    print("Extracted Abstract:", updated_doc.abstract)

    assert updated_doc.title is not None
    assert isinstance(updated_doc.authors, list) or updated_doc.authors is None
    assert updated_doc.abstract is not None