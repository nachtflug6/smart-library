from typing import List, Optional
from smart_library.infrastructure.llm.prompts.base_extraction_prompt import BaseExtractionPrompt
from smart_library.domain.entities.document import Document


class MetadataExtractionPrompt(BaseExtractionPrompt):
    """
    Prompt builder for metadata extraction tasks.
    """

    DEFAULT_TASK = "metadata extraction"
    DEFAULT_INSTRUCTIONS = (
        "Extract bibliographic metadata from the provided document text. "
        "If a field cannot be extracted, set its value to null."
        "Try to be concise and only return the requested fields in JSON format."
    )

    def __init__(self, instructions: Optional[str] = None):
        super().__init__(
            task=self.DEFAULT_TASK,
            instructions=instructions or self.DEFAULT_INSTRUCTIONS
        )

    def get_prompt_for_document(self, text: str) -> str:
        type_map = {
            "Optional[str]": "string",
            "Optional[int]": "integer",
            "Optional[List[str]]": "list of strings",
            "List[str]": "list of strings",
            "str": "string",
            "int": "integer",
        }
        field_types = Document().get_bibliographic_field_types()
        fields_with_types = []
        for name, type_ in field_types.items():
            # Convert type object to string and normalize
            type_str = str(type_)
            # Extract the inner type name using regex
            import re
            match = re.search(r"([A-Za-z]+\[?[A-Za-z, ]*\]?)", type_str)
            if match:
                clean_type = match.group(1).replace(" ", "")
            else:
                clean_type = type_str
            mapped_type = type_map.get(clean_type, "string")
            fields_with_types.append(f"{name} ({mapped_type})")
        return self.get_prompt(text, fields_with_types)

