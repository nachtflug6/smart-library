from smart_library.domain.entities.document import Document
from smart_library.infrastructure.llm.clients.llama3_client import Llama3Client
from smart_library.infrastructure.llm.prompts.llama3_extraction_prompt import Llama3ExtractionPrompt
from smart_library.domain.services.document_service import DocumentService
from smart_library.infrastructure.llm.utils.output_utils import extract_json_from_llm_response

class SimpleMetadataExtractor:
    """
    Extracts metadata from a Document's pages using an LLM and updates the Document.
    """

    DEFAULT_TASK = "metadata extraction"
    DEFAULT_INSTRUCTIONS = (
        "Extract bibliographic metadata from the provided document text. "
        "Return only a single JSON object containing exactly the requested fields. "
        "If a field cannot be extracted directly from the text, set its value to null. "
        "Do not infer or hallucinate missing information. "
        "For list fields, return a JSON list; for all others, return a JSON value. "
        "Do not include explanations, comments, or text outside the JSON object."
    )

    def __init__(self, ollama_url, ollama_model, document_service=None, prompt_instructions=None):
        self.llm = Llama3Client()
        self.document_service = document_service or DocumentService.default_instance()
        self.task = self.DEFAULT_TASK
        self.instructions = prompt_instructions or self.DEFAULT_INSTRUCTIONS
        self.prompt_builder = Llama3ExtractionPrompt(task=self.task, instructions=self.instructions)

    def extract(self, document: Document, group: str = "bibliographic", text: str = None) -> Document:

        # Get the text to analyze
        if text is None:
            pages = self.document_service.get_pages(document.id)
            text = pages[0].full_text if pages and pages[0].full_text else ""

        # Build the prompt
        prompt_dict = self.prompt_builder.get_prompt(text, document, group)

        # Call the LLM
        response = self.llm.chat(prompt_dict)

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
