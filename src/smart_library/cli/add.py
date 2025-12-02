from typer import Argument, Option, echo
from smart_library.application.services.ingestion_service import IngestionService
from smart_library.cli.main import app

@app.command(name="add")
def add(
    path: str = Argument(..., help="Path to the PDF file to ingest"),
    metadata: bool = Option(False, "--metadata", help="Extract metadata during ingestion"),
):
    """Ingest a PDF file and create a Document, Pages, and Text chunks."""

    doc_id = IngestionService.ingest(path, extract_metadata=metadata)
    echo(f"Document ingested successfully. Document ID: {doc_id}")
