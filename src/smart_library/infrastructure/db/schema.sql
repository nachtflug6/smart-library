PRAGMA foreign_keys = ON;

-- ==========================================
-- Base ENTITY table
-- ==========================================
CREATE TABLE entity (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    modified_at TIMESTAMP NOT NULL,
    parent_id TEXT REFERENCES entity(id) ON DELETE CASCADE,
    type TEXT NOT NULL,                   -- Document, Page, Text, Term
    metadata TEXT                          -- JSON as string
);

-- ==========================================
-- DOCUMENT table
-- ==========================================
CREATE TABLE document (
    id TEXT PRIMARY KEY REFERENCES entity(id) ON DELETE CASCADE,
    type TEXT,
    source_path TEXT,
    source_uri TEXT,
    source_format TEXT,
    file_hash TEXT,
    version TEXT,
    title TEXT,
    authors TEXT,          -- store as JSON list
    keywords TEXT,         -- store as JSON list
    doi TEXT,
    publication_date TEXT,
    publisher TEXT,
    venue TEXT,
    year INTEGER,
    page_count INTEGER
);

-- ==========================================
-- PAGE table
-- ==========================================
CREATE TABLE page (
    id TEXT PRIMARY KEY REFERENCES entity(id) ON DELETE CASCADE,
    document_id TEXT REFERENCES document(id) ON DELETE CASCADE,
    page_number INTEGER,
    full_text TEXT,
    token_count INTEGER
);

-- ==========================================
-- TEXT table
-- ==========================================
CREATE TABLE text_entity (
    id TEXT PRIMARY KEY REFERENCES entity(id) ON DELETE CASCADE,
    document_id TEXT REFERENCES document(id) ON DELETE CASCADE,
    page_id TEXT REFERENCES page(id) ON DELETE CASCADE,
    type TEXT,
    index INTEGER,
    content TEXT NOT NULL
);

-- ==========================================
-- TERM table
-- ==========================================
CREATE TABLE term (
    id TEXT PRIMARY KEY REFERENCES entity(id) ON DELETE CASCADE,
    canonical_name TEXT NOT NULL,
    sense TEXT,
    aliases TEXT,        -- JSON list
    domain TEXT,
    definition TEXT,
    related_terms TEXT   -- JSON list of related term IDs
);
