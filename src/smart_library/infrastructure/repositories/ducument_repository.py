from smart_library.domain.entities.document import Document
from smart_library.infrastructure.repositories.base_repository import BaseRepository

class DocumentRepository(BaseRepository):
    table = "documents"
    fields = {
        "id": "TEXT PRIMARY KEY",
        "source_path": "TEXT",
        "title": "TEXT",
        "year": "INTEGER",
        "publisher": "TEXT",
        # add other fields from schema
    }

    def row_to_entity(self, row):
        if not row:
            return None
        return Document(**dict(row))
