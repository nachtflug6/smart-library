import re
import json

def extract_json_from_llm_response(response: str) -> dict:
    """
    Extracts the first JSON object from an LLM response, even if wrapped in text or markdown.
    Returns an empty dict if parsing fails.
    """
    try:
        # Try to find a JSON code block
        match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
        # Fallback: try to find any JSON object in the text
        match = re.search(r"(\{.*\})", response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Last resort: try to load the whole response
        return json.loads(response)
    except Exception as e:
        print("Failed to parse metadata JSON:", e)
        return {}