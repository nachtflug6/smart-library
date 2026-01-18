from typing import Optional, Any
from pathlib import Path
import logging

from .document_app_service import DocumentAppService
from .heading_app_service import HeadingAppService
from .page_app_service import PageAppService
from .text_app_service import TextAppService
from .entity_app_service import EntityAppService
from .embedding_app_service import EmbeddingAppService
from .vector_service import VectorService
from smart_library.infrastructure.grobid.grobid_service import GrobidService
from smart_library.domain.mappers.grobid_domain.snapshop_mapper import build_snapshot


class IngestionAppService:
    """High-level coordinator that persists snapshots (document/headings/pages/texts)
    and handles embedding + vector insertion in a single API.

    The goal is idempotent, best-effort persistence usable by scenarios and the CLI.
    """

    def __init__(self,
                 doc_svc: Optional[DocumentAppService] = None,
                 head_svc: Optional[HeadingAppService] = None,
                 page_svc: Optional[PageAppService] = None,
                 text_svc: Optional[TextAppService] = None,
                 entity_svc: Optional[EntityAppService] = None,
                 embed_svc: Optional[EmbeddingAppService] = None,
                 vec_svc: Optional[VectorService] = None,
                 logger: Optional[logging.Logger] = None,
                 debug: bool = False):
        self.log = logger or logging.getLogger("IngestionAppService")
        # Ensure logger outputs to console at appropriate level
        if not self.log.handlers:
            handler = logging.StreamHandler()
            fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
            handler.setFormatter(fmt)
            self.log.addHandler(handler)
        # Set log level based on debug flag
        self.log.setLevel(logging.DEBUG if debug else logging.WARNING)
        self.doc = doc_svc or DocumentAppService()
        self.head = head_svc or HeadingAppService()
        self.page = page_svc or PageAppService()
        self.text = text_svc or TextAppService()
        self.entity = entity_svc or EntityAppService()
        self.embed = embed_svc or EmbeddingAppService()
        self.vec = vec_svc or VectorService()

    def ensure_entity(self, id: str, kind: str, parent_id: str = None, metadata: dict = None, created_by: str = None) -> bool:
        return self.entity.ensure_exists(id, kind, created_by=created_by, metadata=metadata, parent_id=parent_id)

    def persist_text_with_vector(self, text_obj: Any, embed: bool = True):
        """Persist a `Text` domain object and its vector embedding.

        Returns the text id.
        """
        tid = getattr(text_obj, "id", None)
        if not tid:
            raise ValueError("Text object must have an id")

        # Ensure base entity exists
        try:
            created = self.ensure_entity(tid, "Text", parent_id=getattr(text_obj, "parent_id", None), metadata=getattr(text_obj, "metadata", None), created_by=getattr(text_obj, "created_by", None))
            if created:
                self.log.debug("Created base entity for text %s", tid)
        except Exception:
            self.log.exception("Failed to ensure entity for text %s", tid)

        # Persist text if missing
        try:
            if not self.text.exists(tid):
                self.log.debug("Persisting text %s (len=%d)", tid, len(getattr(text_obj, 'content', '') or ''))
                self.text.add_text(text_obj)
                self.log.info("Text persisted: %s", tid)
            else:
                self.log.debug("Text already exists: %s", tid)
        except Exception:
            self.log.exception("Failed to persist text %s", tid)
            # Re-raise so callers can decide how to handle persistence failure
            raise

        # Create embedding and add vector
        txt_for_embed = getattr(text_obj, "embedding_content", None) or getattr(text_obj, "display_content", None) or getattr(text_obj, "content", "")
        emb = None
        if embed:
            try:
                self.log.debug("Embedding text id=%s len=%d", tid, len(txt_for_embed))
                emb = self.embed.embed(txt_for_embed)
                self.log.debug("Embedding produced length=%d", len(emb) if hasattr(emb, '__len__') else 0)
            except Exception:
                self.log.exception("Embedding failed for text %s, using zero vector", tid)
                emb = [0.0] * 768

        if emb is not None:
            try:
                self.vec.add_vector(tid, emb, created_by=getattr(text_obj, "created_by", None))
                self.log.debug("Vector added for text %s", tid)
            except Exception:
                self.log.exception("Failed to add vector for text %s", tid)

        return tid

    def persist_heading(self, heading_obj: Any):
        hid = getattr(heading_obj, "id", None)
        if not hid:
            raise ValueError("Heading object must have an id")
        try:
            if not self.head.get_heading(hid):
                # Ensure base entity exists via heading repo behavior
                self.head.add_heading(heading_obj)
                self.log.debug("Heading persisted: %s", hid)
        except Exception:
            self.log.exception("Failed to persist heading %s", hid)
            raise
        return hid

    def persist_snapshot(self, snapshot: Any, embed: bool = True):
        """Persist a snapshot produced by the Grobid mapper.

        Idempotent: will skip existing entities.
        """
        doc = getattr(snapshot, "document", None)
        if not doc:
            raise ValueError("Snapshot has no document")

        # Persist document
        try:
            self.log.debug("Persisting snapshot: doc_id=%s title=%s", getattr(doc, "id", None), getattr(doc, "title", None))
            if not self.doc.exists(getattr(doc, "id", None)):
                self.doc.add_document(doc)
                self.log.info("Document persisted: %s", getattr(doc, "id", None))
            else:
                self.log.debug("Document already exists: %s", getattr(doc, "id", None))
        except Exception:
            self.log.exception("Failed to persist document %s", getattr(doc, "id", None))
            raise

        # Headings
        headings = (getattr(snapshot, "headings", None) or [])
        self.log.debug("Snapshot has %d headings", len(headings))
        for h in headings:
            try:
                self.persist_heading(h)
            except Exception:
                self.log.exception("Failed to persist heading %s", getattr(h, 'id', None))

        # Pages/texts
        texts = (getattr(snapshot, "texts", None) or [])
        self.log.debug("Snapshot has %d text objects", len(texts))
        failed_texts = []
        for t in texts:
            try:
                self.persist_text_with_vector(t, embed=embed)
            except Exception:
                tid = getattr(t, 'id', None)
                failed_texts.append(tid)
                self.log.exception("Failed to persist text in snapshot: %s", tid)

        if failed_texts:
            self.log.warning("Some texts failed to persist for document %s: %s", getattr(doc, 'id', None), failed_texts)

        return getattr(doc, "id", None)

    def ingest_from_grobid(self, pdf_path: str | Path, embed: bool = True, source_path: str | None = None):
        """Run Grobid extraction for `pdf_path`, build a domain snapshot, and persist it.

        Returns the document id.
        """
        logger = self.log
        svc = GrobidService()
        xml = None
        try:
            struct, xml = svc.extract_fulltext_with_xml(pdf_path)
        except Exception:
            logger.exception("Grobid extraction failed for %s", pdf_path)
            raise

        try:
            snapshot = build_snapshot(struct, source_path=source_path or str(pdf_path))
        except Exception:
            logger.exception("Failed to build snapshot from Grobid output for %s", pdf_path)
            raise

        doc_id = self.persist_snapshot(snapshot, embed=embed)
        
        # Save the raw XML if we have a valid document ID and XML content
        if doc_id and xml:
            try:
                GrobidService.save_xml(doc_id, xml)
                logger.debug("Saved Grobid XML for document %s", doc_id)
            except Exception:
                logger.exception("Failed to save Grobid XML for document %s", doc_id)
        
        return doc_id

    def close(self):
        for svc in (self.doc, self.head, self.page, self.text):
            try:
                svc.close()
            except Exception:
                pass
