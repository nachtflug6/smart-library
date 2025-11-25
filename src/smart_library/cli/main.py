from typer import Typer, echo, Argument
from smart_library.application.services.ingestion_service import IngestionService

app = Typer(no_args_is_help=True)


@app.command()
def ingest_path(
    path: str = Argument(..., help="Path to the PDF file to ingest")
):
    """Ingest a PDF file and create a Document, Pages, and Text chunks."""
    try:
        doc_id = IngestionService.ingest(path)
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

if __name__ == "__main__":
    app()