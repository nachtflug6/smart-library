
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

		heading_fields = {
			"title": (str,),
			"index": (int, type(None)),
			"page_number": (int,),
		}
		errors = EntityValidation.check_fields_type(kwargs, heading_fields, required_fields=["title"], context_name="Heading")
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
