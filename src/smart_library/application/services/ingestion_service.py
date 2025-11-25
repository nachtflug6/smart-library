# smart_library/application/services/ingestion_service.py

from smart_library.application.pipelines.document_ingestion import ingest_document

class IngestionService:
    """
    Service for document ingestion.
    """

    @staticmethod
    def ingest(path: str):
        """Ingest a document end-to-end."""
        return ingest_document(path)
