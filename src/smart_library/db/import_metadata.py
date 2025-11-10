import json
import sqlite3
from datetime import datetime
from pathlib import Path

def import_document_metadata(jsonl_path: str = "data/jsonl/metadata/document_metadata.jsonl"):
    """
    Import metadata records from a JSONL file into the document_metadata table.
    This does NOT overwrite; it appends new versions.
    """

    jsonl_path = Path(jsonl_path)
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {jsonl_path}")

    db = sqlite3.connect("db/smart_library.db")
    cur = db.cursor()

    with jsonl_path.open() as f:
        for line in f:
            if not line.strip():
                continue

            entry = json.loads(line)

            document_id = entry["document_id"]
            source       = entry.get("source", "llm")     # default
            model        = entry.get("model")
            prompt_ver   = entry.get("prompt_version")

            metadata_json = json.dumps(entry["metadata"], ensure_ascii=False)

            # cached top-level fields for fast querying
            cached_title = entry["metadata"].get("title")
            cached_year  = entry["metadata"].get("year")
            cached_doi   = entry["metadata"].get("doi")

            cur.execute("""
                INSERT INTO document_metadata (
                    document_id,
                    source,
                    created_at,
                    model,
                    prompt_version,
                    metadata_json,
                    title,
                    year,
                    doi
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id,
                source,
                datetime.utcnow().isoformat(),
                model,
                prompt_ver,
                metadata_json,
                cached_title,
                cached_year,
                cached_doi
            ))

    db.commit()
    db.close()
    print("Imported document metadata.")
