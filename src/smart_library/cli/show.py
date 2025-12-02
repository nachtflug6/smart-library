from typer import Argument, echo
from smart_library.application.services.list_service import ListingService
from smart_library.cli.main import app

@app.command(name="show")
def show(
    entity_id: str = Argument(..., help="ID of the document, page, text, or term to show")
):
    """
    Show details for a document, page, text, or term by ID.
    """
    service = ListingService()
    doc = service.repo_doc.get(entity_id)
    if doc:
        echo(f"Document:\n{doc}")
        return
    page = service.repo_page.get(entity_id)
    if page:
        echo(f"Page:\n{page}")
        return
    text = service.repo_text.get(entity_id)
    if text:
        echo(f"Text:\n{text}")
        return
    term = service.repo_term.get(entity_id)
    if term:
        echo(f"Term:\n{term}")
        return
    echo("No entity found with the given ID.")