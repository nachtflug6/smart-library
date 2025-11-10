CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    page_count INTEGER,
    pdf_path TEXT
);


CREATE TABLE IF NOT EXISTS pages (
    document_id TEXT,
    page INTEGER,
    path TEXT,
    PRIMARY KEY (document_id, page)
);


CREATE TABLE IF NOT EXISTS document_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL,
    source TEXT NOT NULL,  -- "llm" or "user"
    timestamp TEXT NOT NULL,
    model TEXT,
    prompt_version TEXT,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);
