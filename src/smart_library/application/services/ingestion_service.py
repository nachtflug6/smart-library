# smart_library/application/services/ingestion_service.py

from smart_library.application.pipelines.document_ingestion import ingest_document

class IngestionService:
    """
    Service for document ingestion.
    """

    @staticmethod
    def ingest(path: str, extract_metadata: bool = False, create_embeddings: bool = True):
        """Ingest a document end-to-end."""
        return ingest_document(path, extract_metadata=extract_metadata, create_embeddings=create_embeddings)
