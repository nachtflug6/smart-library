# src/smart_library/cli/list.py
from typer import Argument, echo
from smart_library.application.services.list_service import ListingService
from smart_library.cli.main import app

@app.command(name="list")
def list(
    what: str = Argument(None, help="What to list: doc, page, text, term, entities"),
    parent_id: str = Argument(None, help="Parent ID (for page, text, term, entities)")
):
    """
    List documents, pages, texts, terms, or all entities.
    Usage:
      smartlib list
      smartlib list doc
      smartlib list page <document_id>
      smartlib list text <page_id>
      smartlib list term <document_id>
      smartlib list entities [<parent_id>]
    """
    service = ListingService()
    if what is None or what == "entities":
        # List all documents, pages, and texts, optionally filtered by parent_id
        echo("Documents:")
        docs = service.list_documents()
        for doc in docs:
            if not parent_id or getattr(doc, "parent_id", None) == parent_id:
                echo(f"  {doc.id} | {getattr(doc, 'title', '')} | {getattr(doc, 'doi', '')}")

        echo("\nPages:")
        pages = service.list_pages(parent_id) if parent_id else service.repo_page.list()
        for page in pages:
            echo(f"  {page.id} | Page {getattr(page, 'page_number', '')} | Parent: {getattr(page, 'parent_id', '')}")

        echo("\nTexts:")
        texts = service.list_texts(parent_id) if parent_id else service.repo_text.list()
        for text in texts:
            echo(f"  {text.id} | {getattr(text, 'type', '')} | {getattr(text, 'chunk_index', '')} | Parent: {getattr(text, 'parent_id', '')}")
        return

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
        echo("Unknown list type. Use one of: doc, page, text, term, entities.")