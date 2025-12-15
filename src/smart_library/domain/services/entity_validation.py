class EntityValidation:
    @staticmethod
    def check_fields_type(kwargs, fields, required_fields=None, context_name="Entity"):
        """
        Utility to check types of fields in `kwargs` against `fields` mapping and
        optionally enforce presence for fields listed in `required_fields`.

        - `fields` should be a dict mapping field_name -> tuple_of_types
        - `required_fields` is an iterable of field names that must be present and not None

        Returns a list of error strings.
        """
        errors = []
        required = set(required_fields or [])
        for field, types in fields.items():
            value = kwargs.get(field)
            if value is None:
                if field in required:
                    errors.append(f"{field} is required for {context_name}")
                continue
            if not isinstance(value, types):
                type_names = " or ".join([t.__name__ for t in types])
                errors.append(f"{field} must be {type_names}, got {type(value).__name__}")
        return errors

    @staticmethod
    def check_entity(id=None, created_by=None, metadata=None, parent_id=None):
        """
        Checks types and raises ValueError if any type is invalid. Returns the validated params as a dict.

        `id` is optional here: if not provided the caller can rely on the
        dataclass default factory to generate an id when constructing the
        entity. We only validate types when values are present.
        """
        errors = []
        if id is not None and not isinstance(id, str):
            errors.append(f"id must be str, got {type(id).__name__}")
        if created_by is not None and not isinstance(created_by, str):
            errors.append(f"created_by must be str or None, got {type(created_by).__name__}")
        if parent_id is not None and not isinstance(parent_id, str):
            errors.append(f"parent_id must be str or None, got {type(parent_id).__name__}")
        if metadata is not None and not isinstance(metadata, dict):
            errors.append(f"metadata must be dict or None, got {type(metadata).__name__}")
        if errors:
            raise ValueError("Entity creation failed due to type errors: " + "; ".join(errors))
        meta = metadata.copy() if metadata else {}
        result = {
            "created_by": created_by,
            "parent_id": parent_id,
            "metadata": meta,
        }
        if id is not None:
            result["id"] = id
        return result
