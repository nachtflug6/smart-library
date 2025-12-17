#!/usr/bin/env python3
"""Scenario: exercise CLI handlers programmatically (ingest -> embed -> search)

This mirrors the grobid_search_ranking scenario but drives it via the CLI
command handler functions (`add` and `search`) so the CLI wiring is exercised.
"""
from pathlib import Path
import sys
import tempfile
import logging

from smart_library.cli.add import add as cli_add
from smart_library.cli.search import search as cli_search
from smart_library import config as _config_module


def scenario_cli_workflow(pdf_path=None, query=None, top_k=5, use_temp_db=True, keep_temp=False):
    logger = logging.getLogger("cli_workflow")
    if not logger.handlers:
        h = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        h.setFormatter(fmt)
        logger.addHandler(h)
    logger.setLevel(logging.DEBUG)

    if pdf_path is None:
        pdf_path = Path(_config_module.DATA_DIR) / "pdf" / "huizhong_test.pdf"
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    tempdir = None
    if use_temp_db:
        if keep_temp:
            tmpdir_path = tempfile.mkdtemp(prefix="smartlib_tmp_")
            tempdir = tmpdir_path
            tmp_db = Path(tempdir) / "temp_smart_library.db"
        else:
            tempobj = tempfile.TemporaryDirectory(prefix="smartlib_tmp_")
            tempdir = tempobj
            tmp_db = Path(tempobj.name) / "temp_smart_library.db"
        _config_module.DB_PATH = tmp_db

        # Initialize schema in the temporary DB so repos can create tables
        try:
            from smart_library.infrastructure.db.db import init_db
            init_db()
        except Exception:
            logger.exception("Failed to initialize temporary DB schema")

    # Call CLI add (which calls IngestionService.ingest)
    logger.info("Ingesting %s via CLI add", pdf_path)
    try:
        cli_add(str(pdf_path), metadata=False)
    except Exception:
        logger.exception("CLI add failed")
        raise

    # Default query if none provided
    if not query:
        query = "sample"

    # Run CLI search
    logger.info("Running CLI search: %s", query)
    try:
        res = cli_search(query, top_k=top_k)
    except Exception:
        logger.exception("CLI search failed")
        res = []

    # Cleanup
    if tempdir is not None and not keep_temp:
        try:
            tempdir.cleanup()
        except Exception:
            pass

    return res


def main():
    try:
        pdf_arg = None
        args = [a for a in sys.argv[1:]]
        if args:
            pdf_arg = args[0]
        scenario_cli_workflow(pdf_path=pdf_arg)
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
