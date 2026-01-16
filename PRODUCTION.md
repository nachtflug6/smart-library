# Smart Library - Production Deployment Guide

This guide provides step-by-step instructions for colleagues to set up and run Smart Library with minimal configuration.

## System Requirements

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **8GB+ RAM** (recommended for embeddings model)
- **GPU** (optional, recommended for faster PDF processing with Grobid)
- ~**20GB disk space** for models and data

## Quick Start (TL;DR)

```bash
# 1. Clone and navigate
git clone <repo-url> smart-library
cd smart-library

# 2. Start all services
docker-compose up -d

# 3. Initialize database (one-time)
docker exec smartlib_dev make init

# 4. Access the application
# UI: http://localhost:5173
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Detailed Setup Instructions

### 1. Prerequisites

Ensure Docker and Docker Compose are installed:

```bash
docker --version    # Should be 20.10 or later
docker-compose --version  # Should be 2.0 or later
```

Install if needed:
- **macOS/Windows**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)

### 2. Clone the Repository

```bash
git clone <repository-url> smart-library
cd smart-library
```

### 3. Configure Environment (Optional)

Create a `.env` file for custom settings:

```bash
cp .env.example .env
```

Available environment variables:
- `GROBID_HOST=grobid:8070` - PDF extraction service
- `OLLAMA_HOST=ollama:11434` - Embeddings/LLM service
- `API_PORT=8000` - FastAPI port
- `UI_PORT=5173` - React UI port

### 4. Start the Services

**Option A: Docker Compose (Recommended)**

```bash
# Start all services (Grobid, Ollama, API, UI)
docker-compose up -d

# Monitor startup (Ollama takes 2-3 min to download models)
docker-compose logs -f ollama

# When you see "Listening on...", services are ready
```

**Option B: Individual Services**

```bash
# Start services
docker-compose up -d grobid ollama devcontainer

# Access the dev container
docker exec -it smartlib_dev bash
```

### 5. Initialize the Database (One-Time)

```bash
# From inside the container or using docker exec
docker exec smartlib_dev make init

# Verify setup
docker exec smartlib_dev make check
```

### 6. Access the Application

Once services are running:

- **Web UI**: http://localhost:5173
  - Upload PDFs
  - Search documents
  - View results with semantic search

- **API Docs**: http://localhost:8000/docs
  - Interactive Swagger documentation
  - Test endpoints directly

- **API**: http://localhost:8000
  - RESTful endpoints for all operations

### 7. First Use

1. **Upload a Document**
   - Click "Upload PDF" in the top-right
   - Select a PDF file
   - Wait for processing (Grobid extracts structure)

2. **Search**
   - Use the global search bar
   - Results show relevant text chunks with page numbers
   - Click "View PDF" to see the source

3. **Feedback Loop**
   - Label results as relevant/irrelevant
   - Use "Rerank with Feedback" to improve results

## Common Tasks

### Stop Services

```bash
docker-compose down

# Keep data persistent
docker-compose down -v # Warning: removes volumes
```

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ollama
docker-compose logs -f grobid
docker-compose logs -f devcontainer
```

### Restart a Service

```bash
docker-compose restart ollama
```

### Reset Database

```bash
docker exec smartlib_dev rm -f data_dev/db/smart_library.db
docker exec smartlib_dev make init
```

### Run CLI Commands

```bash
docker exec smartlib_dev smartlib --help
docker exec smartlib_dev smartlib list
docker exec smartlib_dev smartlib search "query"
```

## Troubleshooting

### Services Won't Start

**Problem**: Container exits immediately
**Solution**:
```bash
docker-compose logs -f devcontainer
docker-compose up -d grobid ollama
# Wait 30 seconds, then
docker-compose up -d devcontainer
```

### "Connection refused" errors

**Problem**: Services not fully initialized
**Solution**:
```bash
# Wait for Ollama to download models (~5 min)
docker-compose logs -f ollama

# Check service health
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### GPU Not Detected

**Problem**: GPU support not working
**Solution**:
```bash
# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.0-runtime-ubuntu20.04 nvidia-smi

# Uncomment GPU sections in docker-compose.yml
# Ensure NVIDIA Container Toolkit is installed
```

### High Memory Usage

**Problem**: Ollama/Grobid consuming too much RAM
**Solution**:
```bash
# Reduce model size (in docker-compose.yml)
# Change: ollama pull llama3.1:8b
# To:     ollama pull llama2:7b
```

### API Slow or Timing Out

**Problem**: Requests taking too long
**Solution**:
```bash
# Check container resources
docker stats smartlib_dev

# Restart services
docker-compose restart
```

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│ (localhost:5173)│
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────┐
│       React + Vite UI                │
│ - Upload PDFs                        │
│ - Search interface                   │
│ - PDF viewer                         │
│ - Result labeling                    │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│     FastAPI REST Server              │
│     (localhost:8000)                 │
│ - Document management                │
│ - Semantic search                    │
│ - PDF processing                     │
│ - Vector storage                     │
└─┬──────────────┬──────────────┬──────┘
  │              │              │
  ▼              ▼              ▼
┌──────┐   ┌──────────┐   ┌──────────┐
│Grobid│   │  Ollama  │   │ SQLite   │
│ PDF  │   │Embeddings│   │ Database │
│Parse │   │  + LLM   │   │          │
└──────┘   └──────────┘   └──────────┘
```

## Performance Notes

- **First run**: Ollama downloads embedding models (~1-2 GB, 2-3 minutes)
- **PDF processing**: ~5-30 seconds per document (depends on size)
- **Semantic search**: ~1-5 seconds (depends on index size)
- **Memory**: ~4GB for Ollama + ~2GB for API/UI
- **GPU**: Accelerates PDF extraction (Grobid) and optional inference

## Features

- **Semantic Search**: Find relevant passages, not just keyword matches
- **PDF Viewer**: Integrated viewer with highlights and navigation
- **Feedback Loop**: Label results to improve ranking
- **Chunked Retrieval**: Exact page and paragraph citations
- **REST API**: Use programmatically in your workflows
- **CLI**: Command-line interface for automation

## Support & Documentation

- **API Docs**: http://localhost:8000/docs (interactive)
- **Architecture**: See `docs/architecture.md`
- **Database Schema**: See `docs/schema.md`
- **CLI Help**: `docker exec smartlib_dev smartlib --help`

## Next Steps

1. Upload your first PDFs
2. Try semantic search
3. Label results to improve ranking
4. Explore the API at http://localhost:8000/docs
5. Check out example queries in `notebooks/`

---

**Questions?** Check the logs, consult `docs/architecture.md`, or review the API documentation.
