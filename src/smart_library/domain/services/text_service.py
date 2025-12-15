from smart_library.domain.entities.text import Text
from smart_library.domain.services.entity_validation import EntityValidation




class TextService:
    @staticmethod
    def check_text(**kwargs):
        entity_keys = ["id", "created_by", "parent_id", "metadata"]
        entity_args = {k: kwargs.get(k) for k in entity_keys}
        entity_checked = EntityValidation.check_entity(**entity_args)

        text_fields = {
            "content": (str,),
            "text_type": (str, type(None)),
            "language": (str, type(None)),
            "order": (int, type(None)),
        }
        errors = EntityValidation.check_fields_type(kwargs, text_fields, context_name="Text")
        if errors:
            raise ValueError("Text creation failed due to type errors: " + "; ".join(errors))
        result = {**entity_checked}
        for k in text_fields:
            if k in kwargs:
                result[k] = kwargs[k]
        return result

    @staticmethod
    def create_text(**kwargs):
        TextService.check_text(**kwargs)
        return Text(**kwargs)
    @classmethod
    def default_instance(cls):
        return cls()
