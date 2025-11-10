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

if __name__ == "__main__":
    app()