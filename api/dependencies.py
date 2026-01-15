"""Shared dependencies for API routes."""
from smart_library.application.services.search_service import SearchService
from smart_library.application.services.document_app_service import DocumentAppService
from smart_library.application.services.text_app_service import TextAppService
from smart_library.application.services.entity_app_service import EntityAppService
from smart_library.application.services.ingestion_app_service import IngestionAppService
from smart_library.application.services.ranking_service import RankingService


def get_search_service() -> SearchService:
    """Get search service instance."""
    return SearchService()


def get_document_service() -> DocumentAppService:
    """Get document service instance."""
    return DocumentAppService()


def get_text_service() -> TextAppService:
    """Get text service instance."""
    return TextAppService()


def get_entity_service() -> EntityAppService:
    """Get entity service instance."""
    return EntityAppService()


def get_ingestion_service(debug: bool = False) -> IngestionAppService:
    """Get ingestion service instance."""
    return IngestionAppService(debug=debug)


def get_ranking_service() -> RankingService:
    """Get ranking service instance."""
    return RankingService()
