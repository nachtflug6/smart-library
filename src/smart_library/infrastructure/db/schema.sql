PRAGMA foreign_keys = ON;

-- =========================================================
-- Base ENTITY table (matches Entity dataclass)
-- =========================================================
DROP TABLE IF EXISTS entity;
CREATE TABLE entity (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    modified_at TIMESTAMP NOT NULL,
    created_by TEXT,
    updated_by TEXT,
    parent_id TEXT REFERENCES entity(id) ON DELETE CASCADE,
    entity_kind TEXT NOT NULL,          -- "Document","Page","Text","Term"
    metadata TEXT                       -- JSON (dict)
);

-- =========================================================
-- DOCUMENT table (matches Document dataclass)
-- =========================================================
DROP TABLE IF EXISTS document;
CREATE TABLE document (
    id TEXT PRIMARY KEY REFERENCES entity(id) ON DELETE CASCADE,
    type TEXT,                          -- classification (research_article, etc.)
    source_path TEXT,
    source_url TEXT,
    source_format TEXT,
    file_hash TEXT,
    version TEXT,
    page_count INTEGER,
    title TEXT,
    authors TEXT,                       -- JSON list
    keywords TEXT,                      -- JSON list
    doi TEXT,
    publication_date TEXT,
    publisher TEXT,
    venue TEXT,
    year INTEGER,
    references TEXT,                    -- JSON list
    citations TEXT                      -- JSON list
);

-- =========================================================
-- PAGE table (matches Page dataclass; relationship via parent_id)
-- parent_id in entity points to Document.id
-- =========================================================
DROP TABLE IF EXISTS page;
CREATE TABLE page (
    id TEXT PRIMARY KEY REFERENCES entity(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    full_text TEXT,
    token_count INTEGER,
    paragraphs TEXT,                    -- JSON list
    sections TEXT,                      -- JSON list
    is_reference_page INTEGER,          -- 0/1
    is_title_page INTEGER,
    has_tables INTEGER,
    has_figures INTEGER,
    has_equations INTEGER
);

-- =========================================================
-- TEXT table (matches Text dataclass; parent_id → Page or Document)
-- =========================================================
DROP TABLE IF EXISTS text_entity;
CREATE TABLE text_entity (
    id TEXT PRIMARY KEY REFERENCES entity(id) ON DELETE CASCADE,
    type TEXT,              -- classification (chunk, summary, etc.)
    index INTEGER,
    content TEXT NOT NULL
);

-- =========================================================
-- TERM table (matches Term dataclass)
-- =========================================================
DROP TABLE IF EXISTS term;
CREATE TABLE term (
    id TEXT PRIMARY KEY REFERENCES entity(id) ON DELETE CASCADE,
    canonical_name TEXT NOT NULL,
    sense TEXT,
    definition TEXT,
    aliases TEXT,           -- JSON list
    domain TEXT,
    related_terms TEXT      -- JSON list
);
