from smart_library.domain.entities.text import Text
from smart_library.domain.constants.text_types import TextType
from smart_library.domain.services.entity_validation import EntityValidation


class TextService:
    @staticmethod
    def check_text(**kwargs):
        entity_keys = ["id", "created_by", "parent_id", "metadata"]
        entity_args = {k: kwargs.get(k) for k in entity_keys}
        entity_checked = EntityValidation.check_entity(**entity_args)

        text_fields = {
            "content": (str,),
            "display_content": (str, type(None)),
            "embedding_content": (str, type(None)),
            "text_type": (TextType,),
            "index": (int, type(None)),
            "character_count": (int, type(None)),
            "token_count": (int, type(None)),
            "page_number": (int, type(None)),
        }
        errors = EntityValidation.check_fields_type(kwargs, text_fields, required_fields=["content"], context_name="Text")
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
