from smart_library.infrastructure.repositories.document_repository import DocumentRepository
from smart_library.infrastructure.repositories.page_repository import PageRepository
from smart_library.infrastructure.repositories.text_repository import TextRepository
from smart_library.infrastructure.repositories.term_repository import TermRepository
from smart_library.infrastructure.repositories.relationship_repository import RelationshipRepository
from smart_library.infrastructure.repositories.entity_repository import EntityRepository



class ListingService:
    def __init__(self):
        self.repo_doc = DocumentRepository()
        self.repo_page = PageRepository()
        self.repo_text = TextRepository()
        self.repo_term = TermRepository()
        self.repo_rel = RelationshipRepository()
        self.repo_ent = EntityRepository()

    def list_documents(self, limit=None):
        return self.repo_doc.list(limit)

    def list_pages(self, doc_id=None, limit=100):
        return self.repo_page.list(doc_id=doc_id, limit=limit)

    def list_texts(self, doc_id=None, page_id=None, limit=100):
        return self.repo_text.list(doc_id=doc_id, page_id=page_id, limit=limit)

    def list_terms(self, limit=50):
        return self.repo_term.list(limit=limit)

    def list_relationships(self, type=None, limit=50):
        return self.repo_rel.list(type=type, limit=limit)

    def list_entities(self, type=None, limit=50):
        return self.repo_ent.list(type=type, limit=limit)
