# src/smart_library/config.py
from __future__ import annotations
import os
from pathlib import Path

DATA_DIR = Path(os.getenv("SMARTLIB_DATA_DIR", "data_dev")).resolve()

DOC_ROOT      = DATA_DIR / "documents"
DOC_PDF_DIR   = DOC_ROOT / "pdf"
DOC_TEXT_DIR  = DOC_ROOT / "text"

JSONL_ROOT    = DATA_DIR / "jsonl"
ENTITIES_JSONL  = JSONL_ROOT / "entities.jsonl"
RELATIONS_JSONL = JSONL_ROOT / "relations.jsonl"