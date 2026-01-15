"""Search API routes."""
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import SearchRequest, SearchResponse, SearchResult, RerankRequest
from api.dependencies import get_search_service, get_text_service, get_entity_service, get_ranking_service, get_document_service
from smart_library.application.services.search_service import SearchService
from smart_library.application.services.text_app_service import TextAppService
from smart_library.application.services.entity_app_service import EntityAppService
from smart_library.application.services.document_app_service import DocumentAppService
from smart_library.application.services.ranking_service import RankingService
from smart_library.application.models.search_response import SearchSession

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Perform similarity search.
    
    Args:
        request: Search query and parameters
        
    Returns:
        Search results with scores
    """
    try:
        results = search_service.similarity_search(
            request.query,
            top_k=request.top_k
        )
        
        if not results:
            return SearchResponse(
                query=request.query,
                results=[],
                total=0
            )
        
        # Convert to response format
        search_results = []
        for i, r in enumerate(results, start=1):
            # Validate that the text entity still exists (not deleted)
            text_id = r.get("id")
            try:
                text = text_service.get_text(text_id)
                if not text:
                    # Skip deleted texts
                    continue
            except Exception:
                # Skip if entity doesn't exist
                continue
            
            search_results.append(
                SearchResult(
                    rank=i,
                    id=text_id,
                    score=r.get("cosine_similarity") or r.get("score") or 0.0,
                    is_positive=False,
                    is_negative=False
                )
            )
        
        # Save session for labeling
        from smart_library.config import DATA_DIR
        import json
        session_file = DATA_DIR / ".search_session.json"
        try:
            # Load existing session to preserve labels
            if session_file.exists():
                session_data = json.loads(session_file.read_text(encoding="utf-8"))
                # If query changed, clear labels
                if session_data.get("query") != request.query:
                    session_data = {"query": request.query, "positive_ids": [], "negative_ids": [], "results": [], "offset": 0}
            else:
                session_data = {"query": request.query, "positive_ids": [], "negative_ids": [], "results": [], "offset": 0}
            
            # Update query and results
            session_data["query"] = request.query
            session_data["results"] = [{"id": r.get("id"), "score": r.get("cosine_similarity") or r.get("score") or 0.0} for r in results]
            
            session_file.parent.mkdir(parents=True, exist_ok=True)
            session_file.write_text(json.dumps(session_data, default=str), encoding="utf-8")
        except Exception:
            pass  # Don't fail search if session save fails
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(search_results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/rerank", response_model=SearchResponse)
async def rerank_search(
    request: RerankRequest,
    ranking_service: RankingService = Depends(get_ranking_service),
    search_service: SearchService = Depends(get_search_service),
    text_service: TextAppService = Depends(get_text_service)
):
    """
    Perform reranked search based on positive/negative feedback.
    
    Args:
        request: Rerank request with query and optional labels
        
    Returns:
        Reranked search results
    """
    try:
        # If no labels provided, try to load from session file
        positive_ids = request.positive_ids
        negative_ids = request.negative_ids
        
        if not positive_ids and not negative_ids:
            from smart_library.config import DATA_DIR
            import json
            session_file = DATA_DIR / ".search_session.json"
            if session_file.exists():
                try:
                    session_data = json.loads(session_file.read_text(encoding="utf-8"))
                    if session_data.get("query") == request.query:
                        positive_ids = session_data.get("positive_ids", [])
                        negative_ids = session_data.get("negative_ids", [])
                except Exception:
                    pass
        
        # Create session with labels
        session = SearchSession(
            query=request.query,
            positive_ids=set(positive_ids),
            negative_ids=set(negative_ids)
        )
        
        # Perform reranking
        response = ranking_service.rerank_from_session(
            session=session,
            embedding_service=search_service.embedding_service,
            text_service=text_service,
            vector_service=search_service.vector_service,
            top_k=request.top_k
        )
        
        # Convert to API response format
        search_results = []
        for r in response.results:
            search_results.append(
                SearchResult(
                    rank=r.rank,
                    id=r.id,
                    score=r.score,
                    is_positive=r.is_positive,
                    is_negative=r.is_negative
                )
            )
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(search_results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rerank failed: {str(e)}")


@router.post("/cleanup/")
async def cleanup_orphaned_vectors(
    search_service: SearchService = Depends(get_search_service)
):
    """
    Clean up orphaned vectors in the vector database.
    This removes vectors that have no corresponding text entity.
    Useful for cleaning up after bulk deletions.
    
    Returns:
        Number of orphaned vectors removed
    """
    try:
        deleted_count = search_service.cleanup_orphaned_vectors()
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} orphaned vectors"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
