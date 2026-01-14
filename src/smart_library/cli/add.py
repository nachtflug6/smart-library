from typer import Argument, Option, echo
from smart_library.cli.main import app


@app.command(name="add")
def add(
    path: str = Argument(..., help="Path to the PDF file to ingest"),
    debug: bool = Option(False, "--debug", help="Enable debug output"),
):
    """Ingest a PDF file using Grobid and persist canonical objects (always embed)."""
    # Use the high-level IngestionAppService which runs Grobid -> snapshot -> persist
    try:
        from smart_library.application.services.ingestion_app_service import IngestionAppService
    except Exception as e:
        echo(f"Failed to import ingestion service: {e}")
        raise

    svc = IngestionAppService(debug=debug)
    try:
        # Always create embeddings/vectors for every text entity
        doc_id = svc.ingest_from_grobid(path, embed=True, source_path=path)
        echo(f"Document ingested successfully. Document ID: {doc_id}")
    except Exception as e:
        echo(f"Ingestion failed: {e}")
        raise

