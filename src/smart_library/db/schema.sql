CREATE TABLE IF NOT EXISTS pages (
    paper_id TEXT,
    page INTEGER,
    path TEXT,
    PRIMARY KEY (paper_id, page)
);
