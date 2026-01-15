"""Document API routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional
import tempfile
import os
import shutil
from api.schemas import (
    DocumentAddRequest,
    DocumentAddResponse,
    DocumentListResponse,
    DocumentDetailResponse,
    TextContentResponse
)
from api.dependencies import (
    get_document_service,
    get_text_service,
    get_ingestion_service
)
from smart_library.application.services.document_app_service import DocumentAppService
from smart_library.application.services.text_app_service import TextAppService
from smart_library.application.services.ingestion_app_service import IngestionAppService

router = APIRouter()


@router.post("/upload/", response_model=DocumentAddResponse)
async def upload_document(
    file: UploadFile = File(...),
    debug: bool = False
):
    """
    Upload and ingest a PDF file.
    
    Args:
        file: Uploaded PDF file
        debug: Enable debug output
        
    Returns:
        Success status and document ID
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        return DocumentAddResponse(
            success=False,
            document_id=None,
            message="Only PDF files are supported"
        )
    
    temp_path = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Ingest the document
        svc = IngestionAppService(debug=debug)
        doc_id = svc.ingest_from_grobid(temp_path, embed=True, source_path=file.filename)
        
        # Store PDF in document storage directory
        try:
            from smart_library.config import DOC_PDF_DIR
            DOC_PDF_DIR.mkdir(parents=True, exist_ok=True)
            # Store with document ID as filename
            pdf_storage_path = DOC_PDF_DIR / f"{doc_id}.pdf"
            shutil.copy(temp_path, pdf_storage_path)
        except Exception as e:
            # Log but don't fail if PDF storage fails
            print(f"Warning: Failed to store PDF: {e}")
        
        return DocumentAddResponse(
            success=True,
            document_id=doc_id,
            message=f"Document uploaded and ingested successfully: {file.filename}"
        )
    
    except Exception as e:
        return DocumentAddResponse(
            success=False,
            document_id=None,
            message=f"Upload failed: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass


@router.post("/add/", response_model=DocumentAddResponse)
async def add_document(
    request: DocumentAddRequest,
    ingestion_service: IngestionAppService = Depends(get_ingestion_service)
):
    """
    Add a new document by ingesting a PDF file from a path.
    
    Args:
        request: Document add request with file path
        
    Returns:
        Success status and document ID
    """
    try:
        pdf_path = Path(request.path)
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.path}")
        
        # Create ingestion service with debug flag
        svc = IngestionAppService(debug=request.debug)
        doc_id = svc.ingest_from_grobid(str(pdf_path), embed=True, source_path=str(pdf_path))
        
        return DocumentAddResponse(
            success=True,
            document_id=doc_id,
            message=f"Document ingested successfully: {doc_id}"
        )
    
    except Exception as e:
        return DocumentAddResponse(
            success=False,
            document_id=None,
            message=f"Ingestion failed: {str(e)}"
        )


@router.get("/pdf/{doc_id}")
async def get_pdf(
    doc_id: str
):
    """
    Get PDF file by document ID.
    
    Args:
        doc_id: Document ID
        
    Returns:
        PDF file
    """
    try:
        from smart_library.config import DOC_PDF_DIR
        pdf_path = DOC_PDF_DIR / f"{doc_id}.pdf"
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"PDF not found for document: {doc_id}")
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve PDF: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = 50,
    document_service: DocumentAppService = Depends(get_document_service)
):
    """
    List all documents.
    
    Args:
        limit: Maximum number of documents to return
        
    Returns:
        List of documents
    """
    try:
        from smart_library.infrastructure.repositories.document_repository import DocumentRepository
        repo = DocumentRepository()
        docs = repo.list(limit=limit)
        
        documents = []
        for doc in docs:
            documents.append({
                "id": doc.id,
                "title": doc.title,
                "authors": doc.authors,
                "year": doc.year,
                "page_count": doc.page_count,
                "source_path": doc.source_path
            })
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/{doc_id}", response_model=DocumentDetailResponse)
async def get_document(
    doc_id: str,
    document_service: DocumentAppService = Depends(get_document_service)
):
    """
    Get document details by ID.
    
    Args:
        doc_id: Document ID
        
    Returns:
        Document details
    """
    try:
        doc = document_service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
        
        return DocumentDetailResponse(
            id=doc.id,
            title=doc.title,
            authors=doc.authors,
            year=doc.year,
            abstract=doc.abstract,
            doi=doc.doi,
            page_count=doc.page_count,
            source_path=doc.source_path
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    document_service: DocumentAppService = Depends(get_document_service)
):
    """
    Delete a document by ID.
    
    Args:
        doc_id: Document ID
        
    Returns:
        Success status
    """
    try:
        from smart_library.infrastructure.repositories.document_repository import DocumentRepository
        from smart_library.infrastructure.db.db import get_connection
        from smart_library.config import DOC_PDF_DIR
        
        # Use a single connection for the entire operation
        conn = get_connection()
        
        # Delete the document (this will remove vectors for descendants via _delete_entity)
        repo = DocumentRepository(conn)
        repo.delete(doc_id)
        # Commit after delete
        conn.commit()
        
        # Then run cleanup to catch any edge cases
        from smart_library.infrastructure.repositories.vector_repository import VectorRepository
        vector_repo = VectorRepository(conn)
        orphans_removed = vector_repo.cleanup_orphaned_vectors()
        
        # Delete associated PDF file
        try:
            pdf_path = DOC_PDF_DIR / f"{doc_id}.pdf"
            if pdf_path.exists():
                pdf_path.unlink()
        except Exception as e:
            print(f"Warning: Failed to delete PDF file for {doc_id}: {e}")
        
        message = f"Document deleted: {doc_id}"
        if orphans_removed > 0:
            message += f" ({orphans_removed} orphaned vectors cleaned up)"
        
        return {"success": True, "message": message}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/text/{text_id}", response_model=TextContentResponse)
async def get_text(
    text_id: str,
    text_service: TextAppService = Depends(get_text_service)
):
    """
    Get text content by ID.
    
    Args:
        text_id: Text entity ID
        
    Returns:
        Text content and metadata
    """
    try:
        text = text_service.get_text(text_id)
        if not text:
            raise HTTPException(status_code=404, detail=f"Text not found: {text_id}")
        
        return TextContentResponse(
            id=text.id,
            content=text.content,
            display_content=text.display_content,
            text_type=text.text_type,
            page_number=text.page_number,
            character_count=text.character_count,
            parent_id=text.parent_id if hasattr(text, 'parent_id') else None,
            metadata=text.metadata if hasattr(text, 'metadata') else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get text: {str(e)}")
