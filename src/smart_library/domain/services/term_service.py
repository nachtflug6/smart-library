from typing import Optional, List
from smart_library.domain.entities.term import Term
from smart_library.domain.services.base_service import BaseService
from smart_library.infrastructure.repositories.term_repository import TermRepository

class TermService(BaseService):
    def __init__(self, term_repo):
        super().__init__(term_repo)
        self.term_repo = term_repo

    @classmethod
    def default_instance(cls):
        repo = TermRepository()
        return cls(repo)

    # CREATE
    def add_term(self, term: Term) -> str:
        self.touch(term)
        return self.term_repo.add(term)

    # READ
    def get_term(self, term_id: str) -> Optional[Term]:
        return self.term_repo.get(term_id)

    def list_terms(self) -> List[Term]:
        return self.term_repo.list_all()

    # UPDATE
    def update_term(self, term: Term):
        self.touch(term)
        return self.term_repo.update(term)

    def update_term_metadata(self, term_id: str, metadata: dict):
        term = self.get_term(term_id)
        if term is None:
            raise ValueError(f"Term not found: {term_id}")
        self.update_metadata(term, metadata)
        self.touch(term)
        return self.term_repo.update(term)

    # DELETE
    def delete_term(self, term_id: str):
        return self.term_repo.delete(term_id)