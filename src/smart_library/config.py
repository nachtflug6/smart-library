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

MIN_PARAGRAPH_LENGTH = 400  # Adjust as needed

class OllamaConfig:
    # both services use the same container now
    HOST = os.getenv("OLLAMA_HOST", "ollama")
    PORT = 11434

    GENERATE_URL = f"http://{HOST}:{PORT}/api/generate"
    CHAT_URL = f"http://{HOST}:{PORT}/api/chat"
    EMBEDDING_URL = f"http://{HOST}:{PORT}/api/embeddings"

    GENERATION_MODEL = "llama3.1:8b"
    EMBEDDING_MODEL = "nomic-embed-text"

class Grobid:
    HOST = os.getenv("GROBID_HOST", "grobid")
    PORT = 8070
    BASE_URL = f"http://{HOST}:{PORT}"
    PROCESSING_TEXT_URL = f"{BASE_URL}/api/processFulltextDocument"
    PROCESSING_HEADER_URL = f"{BASE_URL}/api/processHeaderDocument"


