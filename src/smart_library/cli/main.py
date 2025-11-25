from typer import Typer, echo, Argument, Option
from smart_library.application.services.ingestion_service import IngestionService
from smart_library.application.services.list_service import ListingService

app = Typer(no_args_is_help=True)


@app.command()
def ingest_path(
    path: str = Argument(..., help="Path to the PDF file to ingest"),
    metadata: bool = Option(False, "--metadata", help="Extract metadata during ingestion"),
):
    """Ingest a PDF file and create a Document, Pages, and Text chunks."""
    try:
        doc_id = IngestionService.ingest(path, extract_metadata=metadata)
        echo(f"Document ingested successfully. Document ID: {doc_id}")
    except Exception as e:
        echo(f"Error during ingestion: {e}")

@app.command()
def init_db():
    """Initialize the database schema."""
    from smart_library.infrastructure.db.db import init_db
    try:
        init_db()
        echo("Database initialized successfully.")
    except Exception as e:
        echo(f"Error initializing database: {e}")

@app.command()
def list(
    what: str = Argument(..., help="What to list: doc, page, text, term"),
    parent_id: str = Argument(None, help="Parent ID (for page, text, term)")
):
    """
    List documents, pages, texts, or terms.
    Usage:
      smartlib list doc
      smartlib list page <document_id>
      smartlib list text <page_id>
      smartlib list term <document_id>
    """
    service = ListingService()
    if what == "doc":
        docs = service.list_documents()
        if not docs:
            echo("No documents found.")
            return
        for doc in docs:
            echo(f"{doc.id} | {getattr(doc, 'title', '')} | {getattr(doc, 'doi', '')}")
    elif what == "page":
        if not parent_id:
            echo("Please provide a document ID for listing pages.")
            return
        pages = service.list_pages(parent_id)
        if not pages:
            echo("No pages found for this document.")
            return
        for page in pages:
            echo(f"{page.id} | Page {getattr(page, 'page_number', '')}")
    elif what == "text":
        if not parent_id:
            echo("Please provide a page ID for listing texts.")
            return
        texts = service.list_texts(parent_id)
        if not texts:
            echo("No texts found for this page.")
            return
        for text in texts:
            echo(f"{text.id} | {getattr(text, 'type', '')} | {getattr(text, 'chunk_index', '')}")
    elif what == "term":
        if not parent_id:
            echo("Please provide a document ID for listing terms.")
            return
        terms = service.list_terms(parent_id)
        if not terms:
            echo("No terms found for this document.")
            return
        for term in terms:
            echo(f"{term.id} | {getattr(term, 'name', '')}")
    else:
        echo("Unknown list type. Use one of: doc, page, text, term.")

if __name__ == "__main__":
    app()