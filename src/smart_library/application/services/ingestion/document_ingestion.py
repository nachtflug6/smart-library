from smart_library.domain.entities.document import Document
from smart_library.domain.entities.page import Page
from uuid import uuid4


class DocumentIngestionService:
    def __init__(self, 
                 document_service, 
                 page_service,
                 text_service,
                 metadata_extractor,
                 pdf_reader):
        self.document_service = document_service
        self.page_service = page_service
        self.text_service = text_service
        self.metadata_extractor = metadata_extractor
        self.pdf_reader = pdf_reader

    def import_pdf(self, file_path: str) -> str:
        # 1. Extract raw PDF pages
        raw_pages = self.pdf_reader.read(file_path)

        # 2. Extract metadata (LLM or heuristic)
        meta = self.metadata_extractor.extract(file_path)

        # 3. Create Document entity
        doc = Document(
            id=str(uuid4()),
            source_path=file_path,
            title=meta.title,
            authors=meta.authors,
            metadata=meta.raw,
        )
        doc_id = self.document_service.add_document(doc)

        # 4. Create Page entities
        for i, page_text in enumerate(raw_pages):
            page = Page(
                id=str(uuid4()),
                parent_id=doc_id,
                page_number=i + 1,
                full_text=page_text,
            )
            self.page_service.add_page(page)

        # 5. Create Text chunks for each page (optional)
        for page in self.page_service.get_pages_for_document(doc_id):
            chunks = self.text_service.split_page_into_chunks(page.full_text)
            for chunk in chunks:
                self.text_service.add_text(chunk, parent_id=page.id)

        return doc_id
