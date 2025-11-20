from smart_library.domain.entities.document import Document
from smart_library.domain.entities.page import Page
from smart_library.domain.entities.text import Text
from collections import defaultdict
from typing import Dict, List, Tuple

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

    def ingest(self, pdf_path: str):
        # 1. Extract pages from PDF
        raw_pages = self.pdf_reader.read(pdf_path)

        # 2. Create document
        doc = Document(source_path=pdf_path)
        doc_id = self.document_service.add_document(doc)

        # 3. Create pages + chunks
        for i, page_text in enumerate(raw_pages):
            page = Page(parent_id=doc_id, page_number=i+1, full_text=page_text)
            page_id = self.page_service.add_page(page)

            chunks = self.chunker.chunk(page_text)
            for idx, chunk in enumerate(chunks):
                text = Text(parent_id=page_id, content=chunk, type="chunk", index=idx)
                self.text_service.add_text(text)

        # 4. Optional metadata extraction
        if self.metadata_extractor:
            metadata = self.metadata_extractor.extract(doc.full_text)
            self.document_service.update_document_metadata(doc_id, metadata)

        return doc_id
