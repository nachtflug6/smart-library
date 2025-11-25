from smart_library.domain.entities.document import Document
from smart_library.application.llm.ollama_client import OllamaClient
from smart_library.prompts.metadata_extraction_prompt import get_metadata_extraction_prompt
from smart_library.application.services.document_service import DocumentService
import json

class SimpleMetadataExtractor:
    """
    Extracts metadata from a Document's pages using an LLM and updates the Document.
    """

    def __init__(self, ollama_url, ollama_model, document_service=None):
        self.llm = OllamaClient(ollama_url, ollama_model)
        self.document_service = document_service or DocumentService.default_instance()

    def extract(self, document: Document, prompt_text: str = None) -> Document:
        """
        Extract metadata from the document's pages using an LLM and update the document's fields.
        """
        # Get all pages for the document and concatenate their text
        pages = self.document_service.get_pages(document.id)
        content = "\n".join([p.full_text or "" for p in pages])

        # Prepare the prompt
        doc_fields = [f for f in Document.__dataclass_fields__ if f not in ("id", "created_at", "modified_at", "metadata")]
        structure = "The required fields are: " + ", ".join(doc_fields) + "."
        prompt = (prompt_text or get_metadata_extraction_prompt()) + "\n" + structure + "\n\nDocument Content:\n" + content

        # Call the LLM
        response = self.llm.generate(prompt)
        try:
            metadata = json.loads(response)
        except Exception:
            metadata = {}

        # Update the document fields with extracted metadata
        for key, value in metadata.items():
            if hasattr(document, key):
                setattr(document, key, value)
            else:
                if document.metadata is None:
                    document.metadata = {}
                document.metadata[key] = value

        return document