from typing import List, Optional


class BaseExtractionPrompt:
    """
    Generic prompt builder for extraction tasks (stateful version).
    """

    def __init__(self, task: str, instructions: Optional[str] = None):
        self.task = task
        self.instructions = instructions

    def get_prompt(self, text: str, fields: List[str]) -> str:
        fields_str = "\n".join(f"- {field}" for field in fields)
        base_prompt = (
            f"Task: {self.task}\n"
            f"Extract the following fields:\n"
            f"{fields_str}\n"
            "Return the result as a JSON object.\n\n"
            f"Text to analyze:\n{text}"
        )
        if self.instructions:
            return f"{self.instructions.strip()}\n\n{base_prompt}"
        return base_prompt


if __name__ == "__main__":
    # Smoketest
    task = "metadata extraction"
    instructions = "Extract bibliographic metadata. Only use the fields listed."
    fields = ["title", "authors", "abstract"]
    text = "Deep Learning for AI\nby Jane Doe and John Smith\nAbstract: This paper explores..."

    prompt_builder = BaseExtractionPrompt(task, instructions)
    prompt = prompt_builder.get_prompt(text, fields)
    print("Generated Prompt:\n")
    print(prompt)

