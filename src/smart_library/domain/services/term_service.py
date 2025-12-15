from smart_library.domain.entities.term import Term
from smart_library.domain.constants.term_types import TermType
from smart_library.domain.services.entity_validation import EntityValidation

class TermService:
    @classmethod
    def default_instance(cls):
        return cls()

    @staticmethod
    def check_term(**kwargs):
        entity_keys = ["id", "created_by", "parent_id", "metadata"]
        entity_args = {k: kwargs.get(k) for k in entity_keys}
        entity_checked = EntityValidation.check_entity(**entity_args)

        term_fields = {
            "canonical_name": (str,),
            "type": (TermType,),
            "sense": (str, type(None)),
            "definition": (str, type(None)),
        }
        errors = EntityValidation.check_fields_type(kwargs, term_fields, required_fields=["canonical_name"], context_name="Term")
        if errors:
            raise ValueError("Term creation failed due to type errors: " + "; ".join(errors))
        result = {**entity_checked}
        for k in term_fields:
            if k in kwargs:
                result[k] = kwargs[k]
        return result

    @staticmethod
    def create_term(**kwargs):
        TermService.check_term(**kwargs)
        return Term(**kwargs)