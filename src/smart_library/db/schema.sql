CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    title TEXT,
    venue TEXT,
    year INTEGER,
    page_count INTEGER,
    pdf_path TEXT
);


CREATE TABLE IF NOT EXISTS pages (
    document_id TEXT,
    page INTEGER,
    path TEXT,
    PRIMARY KEY (document_id, page)
);
