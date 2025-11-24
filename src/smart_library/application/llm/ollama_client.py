import requests

class OllamaClient:
    def __init__(self, url, model):
        self.url = url
        self.model = model

    def generate(self, prompt):
        r = requests.post(self.url, json={
            "model": self.model,
            "prompt": prompt,
            "stream": False
        })
        return r.json().get("response", "")

class OllamaEmbeddingModel:
    def __init__(self, url, model):
        self.url = url
        self.model = model

    def embed(self, text):
        r = requests.post(self.url, json={
            "model": self.model,
            "prompt": text
        })
        return r.json().get("embedding")