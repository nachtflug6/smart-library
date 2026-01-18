from typer import Argument, echo
from pathlib import Path
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
        # Also delete the associated PDF file if it exists
        try:
            from smart_library.config import DOC_PDF_DIR, DOC_XML_DIR
            pdf_path = DOC_PDF_DIR / f"{entity_id}.pdf"
            pdf_deleted = False
            if pdf_path.exists():
                pdf_path.unlink()
                pdf_deleted = True
            xml_path = DOC_XML_DIR / f"{entity_id}.xml"
            xml_deleted = False
            if xml_path.exists():
                xml_path.unlink()
                xml_deleted = True
            if pdf_deleted and xml_deleted:
                echo(f"Document {entity_id} deleted (including PDF and XML).")
            elif pdf_deleted and not xml_deleted:
                echo(f"Document {entity_id} deleted (including PDF).")
            elif not pdf_deleted and xml_deleted:
                echo(f"Document {entity_id} deleted (including XML).")
            else:
                echo(f"Document {entity_id} deleted.")
        except Exception as e:
            echo(f"Document {entity_id} deleted, but failed to delete PDF: {e}")
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