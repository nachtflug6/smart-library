"""Label API routes for search result feedback."""
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import LabelRequest, LabelResponse
from pathlib import Path
import json
import os

router = APIRouter()

# Use the same session file as CLI - place in data directory for persistence
from smart_library.config import DATA_DIR
SESSION_FILE = DATA_DIR / ".search_session.json"


def _load_session():
    """Load the cached search session."""
    try:
        if not SESSION_FILE.exists():
            return {"query": "", "positive_ids": [], "negative_ids": [], "results": [], "offset": 0}
        data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        # Ensure sets are loaded as lists (JSON doesn't support sets)
        if "positive_ids" in data and not isinstance(data["positive_ids"], list):
            data["positive_ids"] = list(data["positive_ids"])
        if "negative_ids" in data and not isinstance(data["negative_ids"], list):
            data["negative_ids"] = list(data["negative_ids"])
        return data
    except Exception:
        return {"query": "", "positive_ids": [], "negative_ids": [], "results": [], "offset": 0}


def _save_session(session):
    """Save the search session."""
    try:
        SESSION_FILE.write_text(json.dumps(session, default=str), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save session: {str(e)}")


@router.post("/", response_model=LabelResponse)
async def label_result(request: LabelRequest):
    """
    Label a search result as positive or negative.
    
    Args:
        request: Label request with result ID and label type
        
    Returns:
        Success status
    """
    try:
        session = _load_session()
        
        if not session.get("query"):
            raise HTTPException(
                status_code=400,
                detail="No active search session. Perform a search first."
            )
        
        # Update labels
        if request.label == "pos":
            if request.result_id not in session["positive_ids"]:
                session["positive_ids"].append(request.result_id)
            if request.result_id in session["negative_ids"]:
                session["negative_ids"].remove(request.result_id)
        elif request.label == "neg":
            if request.result_id not in session["negative_ids"]:
                session["negative_ids"].append(request.result_id)
            if request.result_id in session["positive_ids"]:
                session["positive_ids"].remove(request.result_id)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid label. Must be 'pos' or 'neg'."
            )
        
        _save_session(session)
        
        return LabelResponse(
            success=True,
            message=f"Labeled result {request.result_id} as {request.label}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to label result: {str(e)}")


@router.get("/")
async def get_labels():
    """
    Get current labels from the search session.
    
    Returns:
        Current positive and negative labels
    """
    try:
        session = _load_session()
        return {
            "query": session.get("query", ""),
            "positive_ids": session.get("positive_ids", []),
            "negative_ids": session.get("negative_ids", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get labels: {str(e)}")


@router.delete("/")
async def clear_labels():
    """
    Clear all labels from the current search session.
    
    Returns:
        Success status
    """
    try:
        session = _load_session()
        session["positive_ids"] = []
        session["negative_ids"] = []
        _save_session(session)
        
        return {
            "success": True,
            "message": "All labels cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear labels: {str(e)}")
