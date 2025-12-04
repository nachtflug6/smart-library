# src/smart_library/config.py
from __future__ import annotations
import os
from pathlib import Path

DATA_DIR = Path(os.getenv("SMARTLIB_DATA_DIR", "data_dev")).resolve()

DB_PATH     = DATA_DIR / "db/smart_library.db"

DOC_ROOT      = DATA_DIR / "documents"
DOC_PDF_DIR   = DOC_ROOT / "pdf"
DOC_TEXT_DIR  = DOC_ROOT / "text"

JSONL_ROOT    = DATA_DIR / "jsonl"
ENTITIES_JSONL  = JSONL_ROOT / "entities.jsonl"
RELATIONS_JSONL = JSONL_ROOT / "relations.jsonl"

CHUNKER_CONFIG = {
    "max_tokens": 200,
    "overlap": 30,
    "mode": "tokens",  # "tokens", "sentences", "paragraphs"
}

class OllamaConfig:
    # containers on the same Docker network
    GENERATE_HOST = os.getenv("OLLAMA_GENERATE_HOST", "ollama_llama3")
    EMBEDDING_HOST = os.getenv("OLLAMA_EMBED_HOST", "ollama_embed")

    # internal container port always stays 11434
    PORT = 11434

    GENERATE_URL = f"http://{GENERATE_HOST}:{PORT}/api/generate"
    CHAT_URL = f"http://{GENERATE_HOST}:{PORT}/api/chat"
    EMBEDDING_URL = f"http://{EMBEDDING_HOST}:{PORT}/api/embeddings"

    GENERATION_MODEL = "llama3"
    EMBEDDING_MODEL = "nomic-embed-text"

