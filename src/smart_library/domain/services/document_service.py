from smart_library.domain.entities.document import Document
from smart_library.domain.services.entity_validation import EntityValidation
from smart_library.domain.constants.document_types import DocumentType
import os
from smart_library.utils.id_utils import generate_human_id


class DocumentService:
    @classmethod
    def default_instance(cls):
        return cls()

    @staticmethod
    def check_document(**kwargs):
        """
        Checks types for both Entity and Document fields. Raises ValueError if any type is invalid.
        Returns the validated params as a dict.
        """
        # First, check Entity fields using EntityService
        entity_keys = ["id", "created_by", "parent_id", "metadata"]
        entity_args = {k: kwargs.get(k) for k in entity_keys}
        entity_checked = EntityValidation.check_entity(**entity_args)

        errors = []
        # Document-specific fields and their types
        doc_fields = {
            "type": (str, type(None)),
            "source_path": (str, type(None)),
            "source_url": (str, type(None)),
            "source_format": (str, type(None)),
            "file_hash": (str, type(None)),
            "version": (str, type(None)),
            "page_count": (int, type(None)),
            "title": (str, type(None)),
            "authors": (list, type(None)),
            "doi": (str, type(None)),
            "publication_date": (str, type(None)),
            "publisher": (str, type(None)),
            "venue": (str, type(None)),
            "year": (int, type(None)),
            "abstract": (str, type(None)),
        }
        for field, types in doc_fields.items():
            value = kwargs.get(field)
            if field == "type" and value is not None:
                # Accept DocumentType enum or valid string
                if not (isinstance(value, DocumentType) or (isinstance(value, str) and value in DocumentType._value2member_map_)):
                    errors.append(f"type must be a valid DocumentType or string value, got {value}")
            elif value is not None and not isinstance(value, types):
                errors.append(f"{field} must be {types[0].__name__} or None, got {type(value).__name__}")
            # For authors, check list of str
            if field == "authors" and value is not None:
                if not isinstance(value, list) or not all(isinstance(a, str) for a in value):
                    errors.append("authors must be a list of str or None")
        if errors:
            raise ValueError("Document creation failed due to type errors: " + "; ".join(errors))
        # Merge entity_checked and doc fields
        result = {**entity_checked}
        for k in doc_fields:
            if k in kwargs:
                result[k] = kwargs[k]
        return result

    @staticmethod
    def create_document(**kwargs):
        """
        Factory for creating a Document object. Add validation/normalization here if needed.
        Performs type checking before instantiation.
        """
        # Validate fields first
        validated = DocumentService.check_document(**kwargs)

        # Normalize `type`: convert valid string values to DocumentType
        doc_type = validated.get("type")
        if doc_type is not None and isinstance(doc_type, str):
            validated["type"] = DocumentType(doc_type)

        # If a source_path is provided and no citation_key was passed, derive one
        source_path = validated.get("source_path")
        if source_path and not validated.get("citation_key"):
            validated["citation_key"] = os.path.basename(source_path)

        # Ensure a human-readable id for documents when id not explicitly provided
        if not validated.get("id"):
            try:
                validated["id"] = generate_human_id(validated.get("citation_key") or validated.get("title") or "doc")
            except Exception:
                # fallback to default Document id behavior
                pass

        return Document(**validated)
