
from smart_library.domain.entities.heading import Heading
from smart_library.domain.services.entity_validation import EntityValidation


class HeadingService:
	@classmethod
	def default_instance(cls):
		return cls()

	@staticmethod
	def check_heading(**kwargs):
		entity_keys = ["id", "created_by", "parent_id", "metadata"]
		entity_args = {k: kwargs.get(k) for k in entity_keys}
		entity_checked = EntityValidation.check_entity(**entity_args)

		errors = []
		heading_fields = {
			"document_id": (str,),
			"title": (str,),
			"index": (int, type(None)),
			"page_number": (int,),
		}
		for field, types in heading_fields.items():
			value = kwargs.get(field)
			if value is not None and not isinstance(value, types):
				errors.append(f"{field} must be {types[0].__name__}{' or None' if len(types) > 1 else ''}, got {type(value).__name__}")
		if errors:
			raise ValueError("Heading creation failed due to type errors: " + "; ".join(errors))
		result = {**entity_checked}
		for k in heading_fields:
			if k in kwargs:
				result[k] = kwargs[k]
		return result

	@staticmethod
	def create_heading(**kwargs):
		HeadingService.check_heading(**kwargs)
		return Heading(**kwargs)
