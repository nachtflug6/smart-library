class EntityValidation:
    @staticmethod
    def check_fields_type(kwargs, fields, context_name="Entity"):
        """
        Utility to check types of fields in kwargs against a dict of field: (type, ...).
        Returns a list of error strings.
        """
        errors = []
        for field, types in fields.items():
            value = kwargs.get(field)
            if value is not None and not isinstance(value, types):
                # Compose type string for error message
                type_names = " or ".join([t.__name__ for t in types])
                errors.append(f"{field} must be {type_names}, got {type(value).__name__}")
        return errors
    """
    Pure domain service for entity creation logic.
    """

    @staticmethod
    def check_entity(id, created_by=None, metadata=None, parent_id=None):
        """
        Checks types and raises ValueError if any type is invalid. Returns the validated params as a dict.
        """
        errors = []
        if not isinstance(id, str):
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
        return {
            "id": id,
            "created_by": created_by,
            "parent_id": parent_id,
            "metadata": meta
        }
