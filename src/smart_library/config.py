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

class OllamaConfig:
    BASE_URL = "http://host.docker.internal"
    GENERATE_PORT = 11434
    EMBEDDING_PORT = 11436
    
    GENERATE_URL = f"{BASE_URL}:{GENERATE_PORT}/api/generate"
    EMBEDDING_URL = f"{BASE_URL}:{EMBEDDING_PORT}/api/embeddings"

    GENERATION_MODEL = "llama3"
    EMBEDDING_MODEL = "nomic-embed-text"

