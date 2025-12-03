from smart_library.domain.entities.document import Document
from smart_library.infrastructure.llm.clients.ollama_client import OllamaClient
from smart_library.infrastructure.llm.prompts.metadata_extraction_prompt import MetadataExtractionPrompt
from smart_library.domain.services.document_service import DocumentService
from smart_library.infrastructure.llm.utils.output_utils import extract_json_from_llm_response

class SimpleMetadataExtractor:
    """
    Extracts metadata from a Document's pages using an LLM and updates the Document.
    """

    def __init__(self, ollama_url, ollama_model, document_service=None, prompt_instructions=None):
        self.llm = OllamaClient(ollama_url, ollama_model)
        self.document_service = document_service or DocumentService.default_instance()
        self.prompt_builder = MetadataExtractionPrompt(instructions=prompt_instructions)

    def extract(self, document: Document, fields: list[str] = None, text: str = None) -> Document:
        # Use bibliographic fields and types by default
        if fields is None:
            field_types = document.get_bibliographic_field_types()
            fields = [f"{name} ({type_})" for name, type_ in field_types.items()]

        # Get the text to analyze
        if text is None:
            pages = self.document_service.get_pages(document.id)
            text = "\n".join([p.full_text or "" for p in pages])

        # Build the prompt
        prompt = self.prompt_builder.get_prompt(text, fields)

        print("Metadata Extraction Prompt:\n", prompt)

        # Call the LLM
        response = self.llm.generate(prompt)
        print("LLM Response:\n", response)

        # Use the output utils to extract JSON
        metadata = extract_json_from_llm_response(response)
        print("Extracted Metadata:\n", metadata)

        # Update the document fields with extracted metadata
        for key, value in metadata.items():
            if hasattr(document, key):
                setattr(document, key, value)
            else:
                if document.metadata is None:
                    document.metadata = {}
                document.metadata[key] = value

        return document
