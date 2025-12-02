from typing import List, Optional
from smart_library.prompts.base_extraction_prompt import BaseExtractionPrompt


class MetadataExtractionPrompt(BaseExtractionPrompt):
    """
    Prompt builder for metadata extraction tasks.
    """

    DEFAULT_TASK = "metadata extraction"
    DEFAULT_INSTRUCTIONS = (
        "Extract bibliographic metadata from the provided document text. "
        "Return only the fields requested. If a field is missing, use null."
    )

    def __init__(self, instructions: Optional[str] = None):
        super().__init__(
            task=self.DEFAULT_TASK,
            instructions=instructions or self.DEFAULT_INSTRUCTIONS
        )

# Smoketest
if __name__ == "__main__":
    fields = ["title", "authors", "abstract"]
    text = "Deep Learning for AI\nby Jane Doe and John Smith\nAbstract: This paper explores..."
    prompt_builder = MetadataExtractionPrompt()
    prompt = prompt_builder.get_prompt(text, fields)
    print("Generated Metadata Extraction Prompt:\n")
    print(prompt)
