from typer import Typer, Option, echo

app = Typer(no_args_is_help=True)

@app.command("db-init")
def db_init():
    from smart_library.db.init_db import init_db
    init_db()

@app.command("import-documents")
def import_documents_cmd():
    """Import Documents."""
    from smart_library.db.import_entities import import_documents
    import_documents()

@app.command("import-pages")
def import_pages_cmd():
    """Import Pages."""
    from smart_library.db.import_entities import import_pages
    import_pages()

@app.command("import-entities")
def import_entities_cmd():
    """Import all Entities (Documents + Pages)."""
    from smart_library.db.import_entities import import_entities
    import_entities()


@app.command("db-check")
def db_check():
    """Check DB consistency and file links."""
    from smart_library.db.check_db import check_db
    print(check_db())

@app.command("view")
def view_cmd(document_id: str, page: int):
    """View the text of a specific page."""
    from smart_library.db.view import view_page
    view_page(document_id, page)

@app.command("search")
def search_cmd(query: str):
    """Search for text inside all pages."""
    from smart_library.db.search import search
    search(query)


@app.command("onboard-docs")
def onboard_docs_cmd():
    """
    Move incoming PDFs → curated and upsert documents.jsonl
    with document_id, pdf_path, page_count.
    (Title, venue, year remain empty.)
    """
    from smart_library.ingest.onboard import onboard_documents
    onboard_documents()
    echo("Onboarded documents.")


@app.command("onboard-pages")
def onboard_pages_cmd(
    document_id: str = Option(None, help="Process only this document_id")
):
    """
    Extract per-page text for curated PDFs and append to pages.jsonl.
    """
    from smart_library.ingest.onboard import onboard_pages
    onboard_pages(document_id=document_id)
    echo("Onboarded pages.")


@app.command("onboard")
def onboard_all_cmd():
    """
    Full pipeline:
      1) incoming PDFs → curated (documents.jsonl)
      2) extract per-page text (pages.jsonl)
    """
    from smart_library.ingest.onboard import onboard_all
    onboard_all()
    echo("Completed full onboarding pipeline.")

@app.command("llm-metadata-extract")
def llm_metadata_extract_cmd(
    model: str = Option("gpt-5-mini", help="LLM model name."),
    output: str = Option("data/jsonl/joins/documents_metadata_llm.jsonl", help="Output JSONL path."),
):
    """Extract metadata via LLM and write to documents_metadata_llm.jsonl."""
    from pathlib import Path
    from smart_library.pipelines.metadata_extraction import llm_metadata_extract
    
    llm_metadata_extract(model=model, output=Path(output))

@app.command("llm-term-extract")
def llm_term_extract_cmd(
    model: str = Option("gpt-5-mini", help="LLM model name."),
):
    """Extract technical terms from all document pages via LLM."""
    from smart_library.pipelines.term_extraction import llm_term_extract
    llm_term_extract(model=model)

@app.command("terms-verify")
def terms_verify(
    fuzzy: bool = Option(True, help="Use fuzzy verification (thefuzz). If unavailable, falls back to strict."),
    tolerance: int = Option(80, help="Fuzzy tolerance 0..100 (higher=stricter). Ignored if fuzzy is False."),
):
    """
    Verify term occurrences and write *_verified.jsonl outputs.
    Inputs: data/jsonl/joins/terms_raw.jsonl, terms_pages_raw.jsonl, entities/pages.jsonl
    Outputs: data/jsonl/joins/terms_verified.jsonl, terms_pages_verified.jsonl
    """
    from smart_library.pipelines.term_verification import verify_terms_pipeline
    stats = verify_terms_pipeline(fuzzy=fuzzy, tolerance=tolerance)
    echo(f"Verified terms: {stats['terms_verified']}, verified term-page associations: {stats['pages_verified']}")

@app.command("terms-context")
def terms_context(
    window_tokens: int = Option(40, help="Token window size for context."),
    fuzzy: bool = Option(True, help="Use fuzzy fallback."),
    tolerance: int = Option(80, help="Fuzzy tolerance 0..100."),
):
    """Add context snippets around each verified term occurrence."""
    from smart_library.pipelines.term_context_extraction import enrich_term_page_context
    count = enrich_term_page_context(window_tokens=window_tokens, fuzzy=fuzzy, tolerance=tolerance)
    echo(f"Context enrichment completed for {count} rows")

@app.command("terms-classify")
def terms_classify(
    model: str = Option("gpt-5-mini", help="LLM model name."),
    temperature: float = Option(0.2, help="Sampling temperature."),
    batch_size: int = Option(20, help="Items per LLM prompt (one API call per batch)."),
    include_unfound: bool = Option(True, help="Include rows without located context."),
    debug: bool = Option(False, help="Debug mode (process only first batch)."),
    workers: int = Option(1, help="Parallel batches inside each checkpoint."),
    checkpoint_size: int = Option(
        0,
        help="High-level bucket size for checkpointed writes (0 means all rows in one checkpoint).",
    ),
    api_key: str | None = Option(None, help="API key override (defaults to OPENAI_API_KEY)."),
):
    """
    Classify term contexts into tags, context_class, and information_content.
    Writes to data/jsonl/joins/terms_pages_classified.jsonl (JSONL).
    """
    from smart_library.pipelines.term_classification import llm_term_context_classify

    ckpt = None if not checkpoint_size or checkpoint_size <= 0 else checkpoint_size
    count = llm_term_context_classify(
        model=model,
        api_key=api_key,
        temperature=temperature,
        batch_size=batch_size,
        include_unfound=include_unfound,
        debug=debug,
        workers=workers,
        checkpoint_size=ckpt,
    )
    echo(f"Classified rows written: {count}")

if __name__ == "__main__":
    app()