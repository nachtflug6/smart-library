from smart_library.domain.entities.document import Document
from smart_library.application.llm.ollama_client import OllamaClient
from smart_library.prompts.metadata_extraction_prompt import MetadataExtractionPrompt
from smart_library.application.services.document_service import DocumentService
import json

class SimpleMetadataExtractor:
    """
    Extracts metadata from a Document's pages using an LLM and updates the Document.
    """

    def __init__(self, ollama_url, ollama_model, document_service=None, prompt_instructions=None):
        self.llm = OllamaClient(ollama_url, ollama_model)
        self.document_service = document_service or DocumentService.default_instance()
        self.prompt_builder = MetadataExtractionPrompt(instructions=prompt_instructions)

    def extract(self, document: Document, fields: list[str] = None, text: str = None) -> Document:
        """
        Extract metadata from the document's pages using an LLM and update the document's fields.
        :param document: The Document object to update.
        :param fields: List of fields to extract (defaults to all Document fields except id, created_at, modified_at, metadata).
        :param text: Optional text to use for extraction (defaults to all pages' text).
        """
        # Determine which fields to extract
        if fields is None:
            fields = [f for f in Document.__dataclass_fields__ if f not in ("id", "created_at", "modified_at", "metadata")]

        # Get the text to analyze
        if text is None:
            pages = self.document_service.get_pages(document.id)
            text = "\n".join([p.full_text or "" for p in pages])

        # Build the prompt
        prompt = self.prompt_builder.get_prompt(text, fields)

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