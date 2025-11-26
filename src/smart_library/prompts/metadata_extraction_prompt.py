from typing import List, Optional


class BaseExtractionPrompt:
    """
    Generic prompt builder for extraction tasks.
    """

    @staticmethod
    def build(
        text: str,
        task: str,
        fields: List[str],
        instructions: Optional[str] = None
    ) -> str:
        """
        Build a prompt for an extraction task.

        :param text: The text to be queried.
        :param task: The extraction task (e.g., "metadata extraction", "reference extraction").
        :param fields: List of field names to extract.
        :param instructions: Optional extra instructions to prepend.
        :return: The constructed prompt string.
        """
        fields_str = "\n".join(f"- {field}" for field in fields)
        base_prompt = (
            f"Task: {task}\n"
            f"Extract the following fields:\n"
            f"{fields_str}\n"
            "Return the result as a JSON object.\n\n"
            f"Text to analyze:\n{text}"
        )
        if instructions:
            return f"{instructions.strip()}\n\n{base_prompt}"
        return base_prompt
