# core files
touch README.md LICENSE .gitignore pyproject.toml .env.example Makefile

# data hierarchy
mkdir -p data/pdf/{incoming,curated,pages}
mkdir -p data/jsonl/entities
mkdir -p data/jsonl/joins
mkdir -p data/cache
touch data/jsonl/entities/{papers.jsonl,terms.jsonl,term_classes.jsonl,datasets.jsonl,models.jsonl,metrics.jsonl}
touch data/jsonl/joins/{paper_sections.jsonl,paper_terms.jsonl,paper_citations.jsonl,paper_datasets.jsonl,paper_models.jsonl,paper_metrics.jsonl,term_alias_candidates.jsonl,qa_answers.jsonl}

# db
mkdir -p db/migrations db/seeds
touch db/migrations/{0001_init.sql,0002_indexes.sql}
touch db/seeds/demo.sql

# docs
mkdir -p docs
touch docs/{schema.md,architecture.md,api.md}

# notebooks
mkdir -p notebooks
touch notebooks/{01_ingest_demo.ipynb,02_query_examples.ipynb}

# prompts
mkdir -p prompts
touch prompts/{page_classification.md,term_extraction.md,term_verification.md,question_answering.md,summarization.md}

# scripts
mkdir -p scripts
touch scripts/{build_db.sh,export_jsonl.sh,import_jsonl.sh}

# src tree
mkdir -p src/smart_library/{cli,db,extract,entities,joins,qa,utils,vendor}

# top-level package files
touch src/smart_library/{__init__.py,config.py,logging.py}

# CLI
touch src/smart_library/cli/{__init__.py,main.py,imrad_clean.py,ingest.py,terms.py,qa.py,dedupe.py}

# DB
touch src/smart_library/db/{__init__.py,connection.py,schema.sql,upsert.py,queries.py}

# extractors
touch src/smart_library/extract/{__init__.py,pdf_text.py,tables.py,figures.py,imrad_cleaner.py}

# entity definitions
touch src/smart_library/entities/{__init__.py,papers.py,terms.py,datasets.py,models.py,metrics.py,sections.py}

# joins
touch src/smart_library/joins/{__init__.py,paper_sections.py,paper_terms.py,paper_citations.py,paper_datasets.py,paper_models.py,paper_metrics.py,alias_candidates.py}

# QA
touch src/smart_library/qa/{__init__.py,retrieval.py,answer_store.py}

# utils
touch src/smart_library/utils/{__init__.py,io.py,hashing.py,text.py}

# tests
mkdir -p tests
touch tests/{conftest.py,test_imrad_cleaner.py,test_db.py,test_cli.py}
