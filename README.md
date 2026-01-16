# smart-library

**Get started in 5 minutes → See [QUICKSTART.md](QUICKSTART.md)**

Project Goal & Use Cases
------------------------

smart-library is focused on finding relevant, citable passages inside scholarly PDFs — not just matching whole documents. It extracts canonical domain objects (documents, pages, headings, and text chunks) so you can search and retrieve the exact page and paragraph that support a claim. Key use cases:

- Rapid discovery: locate the most relevant paragraph(s) for a query and jump directly to the source page and context.
- Verifiable citations: return the original text snippet + page number so results are directly citable and avoid hallucination when used in downstream summaries.
- Reproducible ingestion: a Grobid-powered pipeline produces normalized snapshots (documents, headings, pages, texts) that can be re-run and audited.
- Semantic search over text chunks: embeddings are computed per chunk and stored in a vector index so similarity search returns focused text hits rather than whole-document matches.

The stack is designed for research and developer workflows where provenance, snippet-level precision, and low hallucination risk matter.

## 🚀 For Colleagues (Try It Out)

**Works on Windows, macOS, and Linux**

### Quick Start (All Platforms)

```bash
git clone <repo-url> smart-library
cd smart-library
```

**Choose one setup method:**

| Platform | Command |
|----------|---------|
| **Windows** | `setup-prod.bat` |
| **macOS/Linux** | `./setup-prod.sh` |
| **Any Platform** | `python setup-prod.py` |

**Opens at:** http://localhost:5173

📖 **Setup Instructions:**
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Platform-Specific Help**: See [PLATFORM_SETUP.md](PLATFORM_SETUP.md)

## 🛠️ For Developers

Getting started — dependencies & services
----------------------------------------

### Prerequisites

This project runs in a dev container that includes all required services (Grobid for PDF processing, Ollama for embeddings). The setup includes:
- **Grobid** (PDF extraction): port `8070`
- **Ollama** (embeddings/LLM): port `11434`
- **FastAPI** (REST API): port `8000`
- **React/Vite** (Web UI): port `5173`

### Quick Start

1. **Start the dev container** (from host machine):

```bash
docker-compose up -d
```

This starts Grobid, Ollama, and the dev container. All development happens inside the container.

2. **Access the dev container**:

```bash
docker ps                       # confirm container name (e.g., smartlib_dev)
docker exec -it smartlib_dev bash
```

Or open the project in VS Code with the Dev Containers extension (recommended).

3. **First-time setup** (inside the container):

```bash
# Initialize database
make init

# Verify setup
make check
```

4. **Start the development servers**:

**Option A: Start both API and UI together** (in separate terminals):
```bash
# Terminal 1: Start API
make api

# Terminal 2: Start UI
make ui
```

**Option B: Use make targets** (view all commands):
```bash
make help
```

5. **Access the application**:

- **Web UI**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Verify Services

Check that external services are running:

```bash
docker-compose logs -f grobid
docker-compose logs -f ollama
```

Notes:
- The `docker-compose.yml` may include GPU/runtime options (e.g., `runtime: nvidia`) — remove or adjust if you don't have an NVIDIA runtime.
- Dependencies are pre-installed in the dev container. If you need to reinstall:
  ```bash
  pip install -r requirements.txt
  cd ui && npm install
  ```

Quick CLI usage
---------------

The CLI provides commands for managing documents, searching, and labeling results.

Initialize the database schema (creates tables including `page_number` on text entities):

```bash
smartlib init
# or: make init
```

Ingest a PDF (creates document, pages, texts, and embeddings/vectors if configured):

```bash
smartlib add /path/to/your/file.pdf
```

Alternatively, use the **Web UI** at http://localhost:5173 to upload PDFs through a graphical interface.

Batch ingestion (optional)
--------------------------

If you want to ingest a whole folder of PDFs at once, run a simple shell loop from the repository root:

```bash
for f in data_dev/pdf/*.pdf; do smartlib add "$f"; done
```

Run a similarity search (top N results):

```bash
smartlib search "your query text" 20
```

Interactive relevance feedback with labeling
--------------------------------------------

The search functionality supports iterative refinement through positive/negative labeling. After running a search, you can label results as relevant (positive) or irrelevant (negative), and the system automatically reruns the search using Rocchio reranking to adjust results based on your feedback.

**Basic workflow:**

1. Run an initial search:
```bash
smartlib search "neural ordinary differential equations"
```

2. Label results by rank number (or entity ID):
```bash
# Label result 1 as positive (relevant)
smartlib label 1 pos

# Label multiple results with the same label
smartlib label 2 3 4 pos

# Label with different labels in one command
smartlib label 1 2 pos 5 6 neg

# Mix of positive and negative examples
smartlib label 1 2 3 pos 4 5 6 neg
```

3. After each label command, the system automatically:
   - Saves your labels to the session (`.search_session.json`)
   - Computes a Rocchio-adjusted query vector using your labeled examples
   - Reruns the search and displays updated results with new similarity scores

**Label persistence:**

- Labels are preserved across repeated searches with the **same query**
- Starting a new search with a **different query** clears previous labels
- This allows iterative refinement: search → label → review → label more → review, etc.

**How it works:**

The system uses Rocchio relevance feedback algorithm:
- Embeddings from positive examples are added to boost the query vector
- Embeddings from negative examples are subtracted to move away from irrelevant content
- Results are reranked based on similarity to the adjusted query vector
- Scores change to reflect the refined search intent

List and inspect entities:

Web UI Features
---------------

The React-based web interface (http://localhost:5173) provides:

- **Document Management**: Upload PDFs, view all documents, delete documents
- **Semantic Search**: Search across document text chunks with similarity-based ranking
- **PDF Viewer**: View PDFs inline in the browser
- **Relevance Feedback**: Label search results as relevant/irrelevant to refine searches
- **Interactive Results**: Click on results to view source text and navigate to the corresponding PDF page

To start the UI:
```bash
make ui                # or: cd ui && npm run dev
```

```bash
smartlib list doc
smartlib show <entity_id>
```

Development without installing
-----------------------------

If you prefer not to install the package, run commands with `PYTHONPATH=src`:

```bash
PYTHONPATH=src python3 -m smart_library.cli.main init
PYTHONPATH=src python3 -m smart_library.cli.main add /path/to/your/file.pdf
PYTHONPATH=src python3 -m smart_library.cli.main search "your query" 5
```
evelopment Commands (Makefile)
-------------------------------

The project includes a Makefile with helpful commands:

```bash
make help       # Show all available commands
make init       # Initialize database (first-time setup)
make check      # Verify all dependencies and setup
make api        # Start API server (port 8000)
make ui         # Start UI development server (port 5173)
```

Docker / Compose Services
-------------------------

The `docker-compose.yml` manages all services:

**Start all services:**
```bash
docker-compose up -d
```

**Check service status:**
```bash
docker-compose ps
```

**View logs:**
```bash
docker-compose logs -f grobid    # PDF extraction service
docker-compose logs -f ollama    # Embedding/LLM service
```

**Service Ports:**
- Grobid REST API: `8070` (configured in `smart_library.config.Grobid`)
- Ollama endpoints: `11434` (configured in `smart_library.config.OllamaConfig`)
- FastAPI: `8000` (API backend)
- React/Vite: `5173` (Web UI)

**Stop services:**
```bash
docker-compose down
```

Notes:
- The `docker-compose.yml` may reference GPU/runtime options (e.g., `runtime: nvidia`) — remove or adjust if you don't have an NVIDIA runtime.
- Dependencies (Python packages, npm modules) are pre-installed in the dev container during build.
- If you prefer to run services manually or use a cloud provider, ensure the host/port values in `smart_library.config` match where Grobid and your embedding service are reachable.
If you prefer to run services manually (or use a cloud provider), ensure the host/port values in
`smart_library.config` match where Grobid and your embedding service are reachable.

Development inside Docker
-------------------------

For development inside the Docker container:

```bash
docker ps                       # confirm container name (e.g., smartlib_dev)
docker exec -it smartlib_dev bash
# then inside container:
python -m pip install -e .
python -m pip install -r requirements.txt
smartlib init
```
