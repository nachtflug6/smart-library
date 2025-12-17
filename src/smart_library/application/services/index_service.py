
from smart_library.infrastructure.embeddings.embedding_service import EmbeddingService
from smart_library.application.services.vector_service import VectorService
from smart_library.domain.services.text_service import TextService
from smart_library.domain.entities.text import Text
from smart_library.domain.constants.text_types import TextType
from smart_library.domain.services.document_service import DocumentService
from smart_library.application.services.document_app_service import DocumentAppService
from smart_library.application.services.text_app_service import TextAppService
import uuid


class IndexService:
	def __init__(self, embedding_service=None, vector_service=None, text_service=None, document_service=None):
		self.embedding_service = embedding_service or EmbeddingService()
		self.vector_service = vector_service or VectorService()
		# Domain text service (factory/validation)
		self.domain_text_service = text_service or TextService.default_instance()
		self.document_service = document_service or DocumentService.default_instance()
		# Application persistence services
		self.doc_app = DocumentAppService()
		self.text_service = TextAppService()

	def index_document(self, title="Untitled Document", **kwargs):
		"""
		Create and add a document to the DB. Returns the document id.
		"""
		doc = self.document_service.create_document(title=title, **kwargs)
		doc_id = self.doc_app.add_document(doc)
		return doc_id

	def index_text(self, text_content, parent_id, created_by=None, text_type=TextType.CHUNK):
		"""
		1. Embed the input text to a vector
		2. Add the vector to the vector DB
		3. Add the text entity to the text DB
		Returns: (text_id, vector_id)
		"""
		if not parent_id:
			raise ValueError("parent_id is required and must reference a Document or Page")
		# 1. Embed
		embedding = self.embedding_service.embed(text_content)
		# 2. Add vector (use a new UUID for id)
		text_id = str(uuid.uuid4())
		self.vector_service.add_vector(text_id, embedding, created_by=created_by)
		# 3. Add text entity
		text_entity = self.domain_text_service.create_text(
			id=text_id,
			parent_id=parent_id,
			content=text_content,
			text_type=text_type,
			created_by=created_by,
			metadata={"embedding": embedding}
		)
		self.text_service.add_text(text_entity)
		return text_id, text_id
