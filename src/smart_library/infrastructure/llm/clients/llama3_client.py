import requests
from smart_library.config import OllamaConfig

class Llama3Client:
    def __init__(self):
        self.url = OllamaConfig.CHAT_URL
        self.model = OllamaConfig.GENERATION_MODEL

    def chat(self, prompt: dict):
        messages = []
        if "system" in prompt:
            messages.append({"role": "system", "content": prompt["system"]})
        if "user" in prompt:
            messages.append({"role": "user", "content": prompt["user"]})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }

        response = requests.post(self.url, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"Ollama error {response.status_code}: {response.text}")

        data = response.json()

        # --- Normalize possible response formats ---
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        if "response" in data:
            return data["response"]
        if "messages" in data:
            for m in reversed(data["messages"]):
                if m.get("role") == "assistant":
                    return m.get("content", "")
        return ""
