"""FastAPI application for smart-library REST API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import search, documents, labels

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
