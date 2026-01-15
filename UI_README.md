# Smart Library - Web UI Setup

## Quick Start

### 1. Start external services

From your **host machine**:
```bash
docker-compose up -d grobid ollama
```

This starts:
- **Grobid** (PDF processing) on port 8070
- **Ollama** (embeddings) on port 11434

### 2. Initialize the database (inside devcontainer)

```bash
smartlib init
```

### 3. Start the API server (Terminal 1)

```bash
cd /workspace
uvicorn api.main:app --reload --port 8000
```

### 4. Start the UI dev server (Terminal 2)

```bash
cd /workspace/ui
npm run dev
```

### 5. Open the web UI

Visit http://localhost:5173 in your browser

---

## Development Setup (Manual)

### API Server

```bash
# Install dependencies
pip install -r api/requirements.txt

# Start API server
cd /workspace
PYTHONPATH=/workspace/src uvicorn api.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### React UI

```bash
# Install dependencies
cd ui
npm install

# Start dev server
npm run dev
```

UI: http://localhost:5173

---

## API Endpoints

### Search
- `POST /api/search/` - Similarity search
- `POST /api/search/rerank` - Reranked search with feedback

### Documents
- `GET /api/documents/` - List all documents
- `GET /api/documents/{id}` - Get document details
- `POST /api/documents/add` - Add new document
- `DELETE /api/documents/{id}` - Delete document
- `GET /api/documents/text/{id}` - Get text content

### Labels
- `POST /api/labels/` - Label a result
- `GET /api/labels/` - Get current labels
- `DELETE /api/labels/` - Clear all labels

---

## Project Structure

```
/workspace/
├── api/                        # FastAPI backend
│   ├── main.py                 # FastAPI app
│   ├── dependencies.py         # Shared dependencies
│   ├── schemas.py              # Pydantic models
│   └── routes/                 # API routes
│       ├── search.py           # Search endpoints
│       ├── documents.py        # Document CRUD
│       └── labels.py           # Labeling
│
├── ui/                         # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   └── services/           # API client
│   └── package.json
│
└── src/smart_library/          # Core library (existing)
```
