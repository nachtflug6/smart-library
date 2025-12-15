from smart_library.domain.entities.term import Term
from smart_library.domain.services.entity_validation import EntityValidation

class TermService:
    @classmethod
    def default_instance(cls):
        return cls()

    @staticmethod
    def check_term(**kwargs):
        entity_keys = ["id", "created_by", "parent_id", "metadata"]
        entity_args = {k: kwargs.get(k) for k in entity_keys}
        entity_checked = EntityService.check_entity(**entity_args)

        errors = []
        term_fields = {
            "name": (str,),
            "definition": (str, type(None)),
            "aliases": (list, type(None)),
            "category": (str, type(None)),
        }
        for field, types in term_fields.items():
            value = kwargs.get(field)
            if value is not None and not isinstance(value, types):
                errors.append(f"{field} must be {types[0].__name__} or None, got {type(value).__name__}")
            if field == "aliases" and value is not None:
                if not isinstance(value, list) or not all(isinstance(a, str) for a in value):
                    errors.append("aliases must be a list of str or None")
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