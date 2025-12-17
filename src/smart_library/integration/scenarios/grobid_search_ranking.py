#!/usr/bin/env python3
"""Scenario: PDF -> Grobid -> persist canonical objects -> embed texts -> similarity search

Usage: PYTHONPATH=src python3 src/smart_library/integration/scenarios/grobid_search_ranking.py
"""
from pathlib import Path
import sys
import traceback
import tempfile
import shutil

from smart_library import config as _config_module
import logging

from smart_library.infrastructure.grobid.grobid_service import GrobidService
from smart_library.domain.mappers.grobid_domain.snapshop_mapper import build_snapshot
from smart_library.integration.scenarios.utils import (
    print_scenario_header,
    print_scenario_footer,
    print_scenario_table_header,
    print_scenario_table_row,
)

from smart_library.infrastructure.repositories.document_repository import DocumentRepository
from smart_library.infrastructure.repositories.heading_repository import HeadingRepository
from smart_library.infrastructure.repositories.text_repository import TextRepository
from smart_library.infrastructure.repositories.vector_repository import VectorRepository
from smart_library.infrastructure.repositories.entity_repository import EntityRepository
from smart_library.infrastructure.embeddings.embedding_service import EmbeddingService
from smart_library.application.services.search_service import SearchService
from smart_library.config import DATA_DIR


def scenario_pdf_search_rank(context=None, pdf_path=None, query=None, top_k=5, reset: bool = True, use_temp_db: bool = True, keep_temp: bool = False):
    logger = logging.getLogger("grobid_search_ranking")
    if not logger.handlers:
        h = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        h.setFormatter(fmt)
        logger.addHandler(h)
    logger.setLevel(logging.DEBUG)
    if pdf_path is None:
        pdf_path = DATA_DIR / "pdf" / "huizhong_test.pdf"
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Extract and build domain snapshot
    logger.info("Extracting PDF via Grobid: %s", pdf_path)
    service = GrobidService()
    try:
        struct = service.extract_fulltext(pdf_path)
    except Exception:
        logger.exception("Grobid extraction failed")
        raise
    logger.info("Building domain snapshot from Grobid output")
    try:
        snapshot = build_snapshot(struct, source_path=str(pdf_path))
    except Exception:
        logger.exception("Snapshot build failed")
        raise

    tempdir = None
    # Optionally use a temporary DB for this scenario run
    if use_temp_db:
        if keep_temp:
            # create a persistent temp dir so it isn't removed automatically
            tmpdir_path = tempfile.mkdtemp(prefix="smartlib_tmp_")
            tempdir = tmpdir_path
            tmp_db = Path(tempdir) / "temp_smart_library.db"
        else:
            tempobj = tempfile.TemporaryDirectory(prefix="smartlib_tmp_")
            tempdir = tempobj
            tmp_db = Path(tempobj.name) / "temp_smart_library.db"
        # override global config DB path for this run
        _config_module.DB_PATH = tmp_db

    # Optionally reinitialize the entire DB (delete DB file and re-run schema)
    if reset or use_temp_db:
        try:
            from smart_library.config import DB_PATH
            from smart_library.infrastructure.db.db import migrate_schema

            # Remove DB file if it exists
            dbp = Path(DB_PATH)
            if dbp.exists():
                dbp.unlink()
            # Recreate schema without attempting to load sqlite-vec (may not be available)
            # Resolve schema path relative to the package root (two levels up from
            # `integration/scenarios` => `smart_library`), not the `integration`
            # directory. The previous path pointed at an invalid location and
            # caused schema initialization to silently fail.
            schema_path = Path(__file__).resolve().parents[2] / "infrastructure" / "db" / "schema.sql"
            from smart_library.infrastructure.db.db import get_connection_with_sqlitevec
            try:
                conn = get_connection_with_sqlitevec(DB_PATH, load_sqlitevec=False)
            except Exception:
                logger.exception("Failed to open DB connection for schema initialization")
                raise
            try:
                if not schema_path.exists():
                    raise FileNotFoundError(f"Schema file not found: {schema_path}")
                sql = schema_path.read_text(encoding="utf-8")
                # Remove sqlite-vec virtual table creation if vec module unavailable
                if "DROP TABLE IF EXISTS vector;" in sql:
                    start_idx = sql.find("DROP TABLE IF EXISTS vector;")
                    next_sep = sql.find("\n-- =========================================================", start_idx)
                    if next_sep != -1:
                        sql = sql[:start_idx] + sql[next_sep:]
                conn.executescript(sql)
                conn.commit()
            except Exception:
                logger.exception("Failed to initialize schema from %s", schema_path)
                raise
            finally:
                conn.close()
            # Recreate repo connections to pick up the new DB file
            pass
        except Exception:
            pass

    # Repos / services (create after optional reset so connections target the correct DB)
    repo_doc = DocumentRepository()
    repo_head = HeadingRepository()
    repo_text = TextRepository()
    embed_svc = EmbeddingService()
    vec_repo = VectorRepository.default_instance()
    search_svc = SearchService()
    logger.info("Repositories and services initialized. DB: %s", getattr(_config_module, 'DB_PATH', '<unknown>'))

    # Persist document if missing
    doc = snapshot.document
    logger.info("Persisting document %s", getattr(doc, 'id', None))
    try:
        if not repo_doc.get(doc.id):
            repo_doc.add(doc)
            logger.debug("Document persisted: %s", doc.id)
        else:
            logger.debug("Document already exists: %s", doc.id)
    except Exception:
        logger.exception("Failed to persist document")
        raise

    # Persist headings
    for h in (snapshot.headings or []):
        if not repo_head.get(h.id):
            repo_head.add(h)

    # Persist pages (if present in snapshot) and texts + vectors
    for t in (snapshot.texts or []):
        # Persist text entity (and underlying entity) if missing
        try:
            if not repo_text.get(t.id):
                repo_text.add(t)
                logger.debug("Text persisted: %s (chars=%s)", t.id, len(getattr(t, 'content', '') or ''))
            else:
                logger.debug("Text already exists: %s", t.id)
        except Exception:
            logger.exception("Failed to persist text %s", t.id)
            raise

        # Create embedding and add vector (vector repo will ensure base entity exists)
        txt_for_embed = getattr(t, "embedding_content", None) or getattr(t, "display_content", None) or getattr(t, "content", "")
        try:
            logger.debug("Embedding text id=%s len=%d", t.id, len(txt_for_embed))
            emb = embed_svc.embed(txt_for_embed)
            logger.debug("Embedding produced length=%d", len(emb) if hasattr(emb, '__len__') else 0)
        except Exception:
            logger.exception("Embedding failed for text %s, using zero vector", t.id)
            emb = [0.0] * 768
        try:
            vec_repo.add_vector(t.id, emb, created_by=getattr(t, "created_by", None))
            logger.debug("Vector added for text %s", t.id)
        except Exception:
            logger.exception("Failed to add vector for text %s", t.id)
            # Some environments may not have sqlite-vec; ignore vector insertion failures here
            pass

    # If no query provided, use a short text from the document for demonstration
    if not query:
        # pick first text as query fallback
        query = "".join([ (snapshot.texts[0].content[:200] if snapshot.texts else "") ])

    # Run similarity search
    logger.info("Running similarity search top_k=%d", top_k)
    try:
        results = search_svc.similarity_search(query, top_k=top_k)
        logger.info("Similarity search returned %d results", len(results) if results else 0)
    except Exception:
        logger.exception("Similarity search failed")
        results = []

    # Display ranked results with doc title, authors, year, page, snippet
    print_scenario_header("GROBID -> Persist -> Embed -> Search", goal="Rank texts similar to a query and display context")
    print_scenario_table_header(["Rank", "Doc Title", "Authors", "Year", "Page", "Cosine", "Snippet"])

    # Collapse duplicates by parent document so the scenario displays one hit per document
    seen_docs = set()
    unique_rows = []
    entity_repo = EntityRepository()
    for r in results:
        tid = r.get("id")
        score = r.get("cosine_similarity") or r.get("cosine") or 0.0
        txt = repo_text.get(tid)
        if not txt:
            continue

        # normalize text fields
        if isinstance(txt, dict):
            meta = txt.get("metadata") or {}
            parent = txt.get("parent_id")
            content = txt.get("content") or txt.get("display_content") or ""
        else:
            meta = getattr(txt, "metadata", {}) or {}
            parent = getattr(txt, "parent_id", None)
            content = getattr(txt, "content", None) or getattr(txt, "display_content", None) or ""

        # Determine document id: text -> parent (page or document) -> if parent is a page, its parent_id is the document id
        document_id = None
        try:
            if parent:
                parent_entity = entity_repo.get(parent)
                if parent_entity:
                    # If parent is a page, its parent_id points to the document
                    parent_of_parent = parent_entity.get("parent_id")
                    if parent_of_parent:
                        document_id = parent_of_parent
                    else:
                        # parent itself may be the document
                        document_id = parent_entity.get("id") or parent
                else:
                    document_id = parent
        except Exception:
            document_id = parent

        if document_id in seen_docs:
            continue
        seen_docs.add(document_id)

        # gather display fields
        snippet = (content.strip().replace("\n", " ")[:120] + ("..." if len(content) > 120 else ""))
        page_num = meta.get("page_number") or meta.get("page") or ""
        doc_row = repo_doc.get(document_id) if document_id else None
        doc_title = ""
        authors = ""
        year = ""
        if doc_row:
            if isinstance(doc_row, dict):
                doc_title = doc_row.get("title") or ""
                authors = doc_row.get("authors") or ""
                year = doc_row.get("year") or ""
            else:
                doc_title = getattr(doc_row, "title", "") or ""
                authors = getattr(doc_row, "authors", None) or ""
                year = getattr(doc_row, "year", None) or ""

        unique_rows.append((doc_title, authors, year, page_num, score, snippet))
        if len(unique_rows) >= top_k:
            break

    # Print unique rows
    rank = 0
    for doc_title, authors, year, page_num, score, snippet in unique_rows:
        rank += 1
        print_scenario_table_row([f"{rank}", doc_title, (", ".join(authors) if isinstance(authors, list) else authors), year, page_num, f"{score:.4f}", snippet])

    print_scenario_footer()
    # Cleanup temporary DB if requested. If `keep_temp` was set the temp dir is preserved.
    if tempdir is not None:
        try:
            # close open connections held by repos
            for repo in (repo_doc, repo_head, repo_text):
                try:
                    repo.conn.close()
                except Exception:
                    pass
        finally:
            if use_temp_db and not keep_temp:
                try:
                    # tempdir is a TemporaryDirectory object
                    tempdir.cleanup()
                except Exception:
                    pass
            else:
                # tempdir is a persistent path string when keep_temp=True
                logger.info("Preserved temporary DB at: %s", getattr(_config_module, 'DB_PATH', '<unknown>'))
    return results


def main():
    try:
        pdf_arg = None
        args = [a for a in sys.argv[1:]]
        keep_temp_flag = False
        if "--keep-temp" in args:
            keep_temp_flag = True
            args.remove("--keep-temp")
        if args:
            pdf_arg = args[0]
        # Always run scenarios against a temporary DB and reset it.
        scenario_pdf_search_rank(None, pdf_path=pdf_arg, reset=True, use_temp_db=True, keep_temp=keep_temp_flag)
    except Exception:
        print("Error running scenario:\n", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
