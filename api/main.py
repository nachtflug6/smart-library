"""FastAPI application for smart-library REST API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import search, documents, labels
from pathlib import Path
import logging

app = FastAPI(
    title="Smart Library API",
    description="REST API for document ingestion, search, and labeling",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup if it doesn't exist."""
    from smart_library.config import DB_PATH, DOC_PDF_DIR
    from smart_library.infrastructure.db.db import init_db
    
    logger = logging.getLogger("api.startup")
    
    # Create data directories if they don't exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PDF_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize database if it doesn't exist
    if not DB_PATH.exists():
        logger.info("Database not found, initializing...")
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    else:
        logger.info(f"Database found at {DB_PATH}")

# Include routers
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(labels.router, prefix="/api/labels", tags=["labels"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Smart Library API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
