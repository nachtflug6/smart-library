from smart_library.domain.entities.document import Document
from smart_library.domain.entities.page import Page
from smart_library.domain.entities.text import Text
from smart_library.application.pdf.pdf_reader import PDFReader
from smart_library.application.services.document_service import DocumentService
from smart_library.application.services.page_service import PageService
from smart_library.application.services.text_service import TextService
from smart_library.application.services.chunker import TextChunker
from smart_library.application.pipelines.metadata_extraction import SimpleMetadataExtractor
from collections import defaultdict
from typing import Dict, List, Tuple
from smart_library.config import OllamaConfig
from smart_library.application.llm.ollama_client import OllamaClient, OllamaEmbeddingModel
from smart_library.application.services.embedding_service import EmbeddingService

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
        self.pdf_reader = pdf_reader
        self.chunker = chunker
        self.metadata_extractor = metadata_extractor
        self.embedding_service = embedding_service

    def ingest(self, pdf_path: str, extract_metadata: bool = False, create_embeddings: bool = True):
        # 1. Extract pages from PDF
        raw_pages = self.pdf_reader.read(pdf_path)

        # 2. Create document
        doc = Document(source_path=pdf_path)
        doc_id = self.document_service.add_document(doc)

        # 3. Create pages + chunks
        first_page_id = None
        first_page_text = None
        page_ids = []
        for i, page_text in enumerate(raw_pages):
            page = Page(parent_id=doc_id, page_number=i+1, full_text=page_text)
            page_id = self.page_service.add_page(page)
            page_ids.append(page_id)
            if i == 0:
                first_page_id = page_id
                first_page_text = page_text

            chunks = self.chunker.chunk(page_text)
            chunk_ids = []
            for idx, chunk in enumerate(chunks):
                text = Text(parent_id=page_id, content=chunk, text_type="chunk", index=idx)
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
                doc.full_text = first_page_text
                doc_with_metadata = self.metadata_extractor.extract(doc)
                self.document_service.update_document_metadata(doc_id, doc_with_metadata.metadata)
                # Optionally update other fields (title, authors, etc.) if needed

        return doc_id

def ingest_document(pdf_path: str, extract_metadata: bool = False, create_embeddings: bool = True):
    """
    Factory function to wire up dependencies and run ingestion.
    """
    document_service = DocumentService.default_instance()
    page_service = PageService.default_instance()
    text_service = TextService.default_instance()
    pdf_reader = PDFReader()
    chunker = TextChunker()
    metadata_extractor = SimpleMetadataExtractor(
        ollama_url=OllamaConfig.GENERATE_URL,
        ollama_model=OllamaConfig.GENERATION_MODEL
    )
    # Instantiate embedding service (you may need to wire up the repos/llm_client as in your project)
    embedding_service = EmbeddingService.default_instance()

    ingestion_service = DocumentIngestionService(
        document_service=document_service,
        page_service=page_service,
        text_service=text_service,
        pdf_reader=pdf_reader,
        chunker=chunker,
        metadata_extractor=metadata_extractor,
        embedding_service=embedding_service,
    )
    return ingestion_service.ingest(pdf_path, extract_metadata=extract_metadata, create_embeddings=create_embeddings)

ollama_client = OllamaClient(
    url=OllamaConfig.GENERATE_URL,
    model=OllamaConfig.GENERATION_MODEL
)

ollama_embed = OllamaEmbeddingModel(
    url=OllamaConfig.EMBEDDING_URL,
    model=OllamaConfig.EMBEDDING_MODEL
)
