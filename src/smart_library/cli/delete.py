from typer import Argument, echo
from smart_library.application.services.list_service import ListingService
from smart_library.cli.main import app

@app.command(name="delete")
def delete(
    entity_id: str = Argument(..., help="ID of the document, page, text, or term to delete")
):
    """
    Delete a document, page, text, or term by ID.
    """
    service = ListingService()
    if service.repo_doc.get(entity_id):
        service.repo_doc.delete(entity_id)
        echo(f"Document {entity_id} deleted.")
        return
    if service.repo_page.get(entity_id):
        service.repo_page.delete(entity_id)
        echo(f"Page {entity_id} deleted.")
        return
    if service.repo_text.get(entity_id):
        service.repo_text.delete(entity_id)
        echo(f"Text {entity_id} deleted.")
        return
    if service.repo_term.get(entity_id):
        service.repo_term.delete(entity_id)
        echo(f"Term {entity_id} deleted.")
        return
    echo("No entity found with the given ID.")