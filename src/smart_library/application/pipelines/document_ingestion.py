from smart_library.domain.entities.document import Document
from smart_library.domain.entities.page import Page
from smart_library.domain.entities.text import Text
from smart_library.utils.pdf_reader import PDFReader
from smart_library.domain.services.document_service import DocumentService
from smart_library.domain.services.page_service import PageService
from smart_library.domain.services.text_service import TextService
from smart_library.application.services.document_app_service import DocumentAppService
from smart_library.application.services.page_app_service import PageAppService
from smart_library.application.services.text_app_service import TextAppService
from smart_library.utils.chunker import TextChunker
from smart_library.application.pipelines.metadata_extraction import SimpleMetadataExtractor
from collections import defaultdict
from typing import Dict, List, Tuple
from smart_library.config import OllamaConfig
from smart_library.infrastructure.llm.clients.ollama_client import OllamaClient
from smart_library.infrastructure.embeddings.embedding_client import OllamaEmbeddingModel
from smart_library.infrastructure.embeddings.embedding_service import EmbeddingService

class DocumentIngestionService:
    def __init__(self, 
                 document_service,
                 page_service,
                 text_service,
                 pdf_reader,
                 chunker,
                 metadata_extractor=None,
                 embedding_service=None):
                 
        self.document_service = document_service
        self.page_service = page_service
        self.text_service = text_service
        # Application-level persistence services (optional)
        self.document_app = None
        self.page_app = None
        self.text_app = None
        self.pdf_reader = pdf_reader
        self.chunker = chunker
        self.metadata_extractor = metadata_extractor
        self.embedding_service = embedding_service

    def ingest(self, pdf_path: str, extract_metadata: bool = False, create_embeddings: bool = True):
        # 1. Extract pages from PDF
        raw_pages = self.pdf_reader.read(pdf_path)

        # 2. Create document (use domain service factory to ensure citation_key/human id)
        doc = self.document_service.create_document(source_path=pdf_path)
        # Persist document via application-level service if available, else try domain service
        if getattr(self, 'document_app', None):
            doc_id = self.document_app.add_document(doc)
        else:
            doc_id = self.document_service.add_document(doc)

        # 3. Create pages + chunks
        first_page_id = None
        first_page_text = None
        page_ids = []
        for i, page_text in enumerate(raw_pages):
            page = Page(parent_id=doc_id, page_number=i+1, full_text=page_text)
            if getattr(self, 'page_app', None):
                page_id = self.page_app.add_page(page)
            else:
                page_id = self.page_service.add_page(page)
            page_ids.append(page_id)
            if i == 0:
                first_page_id = page_id
                first_page_text = page_text

            chunks = self.chunker.chunk(page_text)
            chunk_ids = []
            for idx, chunk in enumerate(chunks):
                text = Text(parent_id=page_id, content=chunk, text_type="chunk", index=idx)
                if getattr(self, 'text_app', None):
                    text_id = self.text_app.add_text(text)
                else:
                    text_id = self.text_service.add_text(text)
                chunk_ids.append(text_id)

                # Create embedding for each chunk
                if self.embedding_service and create_embeddings:
                    self.embedding_service.embed_text(text_id)

            # Aggregate chunk embeddings to page embedding
            if self.embedding_service and create_embeddings and chunk_ids:
                self.embedding_service.aggregate_to_page_embedding(page_id, chunk_ids)

        # Aggregate page embeddings to document embedding
        if self.embedding_service and create_embeddings and page_ids:
            self.embedding_service.aggregate_to_document_embedding(doc_id, page_ids)

        # 4. Optional metadata extraction (only on first page)
        if extract_metadata and first_page_text:
            if self.metadata_extractor:
                doc_with_metadata = self.metadata_extractor.extract(doc)
                self.document_service.update_document(doc_with_metadata)
                # Optionally update other fields (title, authors, etc.) if needed

        return doc_id

def ingest_document(pdf_path: str, extract_metadata: bool = False, create_embeddings: bool = True):
    """
    Factory function to wire up dependencies and run ingestion.
    """
    document_service = DocumentService.default_instance()
    page_service = PageService.default_instance()
    text_service = TextService.default_instance()
    # Application persistence services
    document_app = DocumentAppService()
    page_app = PageAppService()
    text_app = TextAppService()
    pdf_reader = PDFReader()
    chunker = TextChunker()
    metadata_extractor = SimpleMetadataExtractor(
        ollama_url=OllamaConfig.GENERATE_URL,
        ollama_model=OllamaConfig.GENERATION_MODEL
    )
    # Instantiate embedding service only if requested. Some environments may not
    # have the external embedding service available; allow disabling embeddings
    # via `create_embeddings=False`.
    embedding_service = None
    if create_embeddings:
        try:
            embedding_service = EmbeddingService()
        except Exception:
            embedding_service = None

    ingestion_service = DocumentIngestionService(
        document_service=document_service,
        page_service=page_service,
        text_service=text_service,
        pdf_reader=pdf_reader,
        chunker=chunker,
        metadata_extractor=metadata_extractor,
        embedding_service=embedding_service,
    )
    # attach application persistence services so ingestion uses them
    ingestion_service.document_app = document_app
    ingestion_service.page_app = page_app
    ingestion_service.text_app = text_app
    # Use app services to persist created entities in the pipeline
    doc_id = ingestion_service.ingest(pdf_path, extract_metadata=extract_metadata, create_embeddings=create_embeddings)
    return doc_id

ollama_client = OllamaClient(
    url=OllamaConfig.GENERATE_URL,
    model=OllamaConfig.GENERATION_MODEL
)

ollama_embed = OllamaEmbeddingModel(
    url=OllamaConfig.EMBEDDING_URL,
    model=OllamaConfig.EMBEDDING_MODEL
)
