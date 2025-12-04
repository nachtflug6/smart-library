from smart_library.infrastructure.llm.prompts.base_extraction_prompt import BaseExtractionPrompt
from typing import List

class Llama3ExtractionPrompt(BaseExtractionPrompt):
    """
    Builds prompts optimized for Llama 3 / Llama 3.1 instruct models.
    """

    SYSTEM_INSTRUCTIONS = """
You are an information extraction system. 
Extract only the requested metadata fields from the document text.

REQUIREMENTS:
- Output must be *valid JSON*, with double quotes.
- Output must contain *exactly* the requested fields.
- If a field cannot be extracted, set its value to null.
- Do NOT infer or hallucinate missing information.
- Do NOT output explanations, comments, or text outside the JSON.
- Do NOT surround JSON with markdown or other formatting.
- For each field, follow the type and format as specified.
"""

    def get_prompt(self, text: str, document, group: str) -> dict:
        """
        Returns a dict structured as Llama-3 expects:
        { "system": "...", "user": "..." }
        """
        # Get field metadata for the group
        fields_with_types = []
        for name, field_obj in document.__dataclass_fields__.items():
            if field_obj.metadata.get("group") == group:
                llm_type = field_obj.metadata.get("llm_type", "string")
                fmt = field_obj.metadata.get("format", "")
                fields_with_types.append(f"{name} ({llm_type}) - {fmt}")

        # Build the JSON example schema (field names only)
        example_json = "{\n" + ",\n".join(
            f'  "{field.split(" ")[0]}": null' for field in fields_with_types
        ) + "\n}"

        fields_str = "\n".join(f"- {field}" for field in fields_with_types)

        user_prompt = f"""
Extract the following fields (type and format in parentheses):
{fields_str}

Return only valid JSON in this format:
{example_json}

Text to analyze:
{text}
"""

        return {
            "system": self.SYSTEM_INSTRUCTIONS.strip(),
            "user": user_prompt.strip(),
        }


if __name__ == "__main__":
    from smart_library.domain.entities.document import Document

    # Create a toy document instance
    doc = Document(
        title=None,
        authors=None,
        keywords=None,
        doi=None,
        publication_date=None,
        publisher=None,
        venue=None,
        year=None,
        abstract=None
    )

    # Example text to analyze
    text = "Deep Learning for AI\nby Jane Doe and John Smith\nAbstract: This paper explores..."

    # Instantiate the prompt builder
    prompt_builder = Llama3ExtractionPrompt("Extract bibliographic metadata")

    # Build the prompt for the bibliographic group
    prompt_dict = prompt_builder.get_prompt(text, doc, "bibliographic")

    print("=== Llama3ExtractionPrompt Smoketest ===")
    print("System message:\n", prompt_dict["system"])
    print("\nUser message:\n", prompt_dict["user"])

    print(prompt_dict)
