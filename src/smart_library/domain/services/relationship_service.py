
from smart_library.domain.entities.relationship import Relationship
from smart_library.domain.constants.relationship_types import RelationshipType
from smart_library.domain.services.entity_validation import EntityValidation

class RelationshipService:
	@classmethod
	def default_instance(cls):
		return cls()

	@staticmethod
	def check_relationship(**kwargs):
		entity_keys = ["id", "created_by", "parent_id", "metadata"]
		entity_args = {k: kwargs.get(k) for k in entity_keys}
		entity_checked = EntityValidation.check_entity(**entity_args)

		rel_fields = {
			"source_id": (str,),
			"target_id": (str,),
			"type": (RelationshipType,),
		}
		# Validate relationship-specific fields; require all three
		errors = EntityValidation.check_fields_type(kwargs, rel_fields, required_fields=["source_id", "target_id", "type"], context_name="Relationship")
		if errors:
			raise ValueError("Relationship creation failed due to type errors: " + "; ".join(errors))
		result = {**entity_checked}
		for k in rel_fields:
			if k in kwargs:
				result[k] = kwargs[k]
		return result

	@staticmethod
	def create_relationship(**kwargs):
		RelationshipService.check_relationship(**kwargs)
		return Relationship(**kwargs)
