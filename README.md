# smart-library

Project Goal & Use Cases
------------------------

smart-library is focused on finding relevant, citable passages inside scholarly PDFs — not just matching whole documents. It extracts canonical domain objects (documents, pages, headings, and text chunks) so you can search and retrieve the exact page and paragraph that support a claim. Key use cases:

- Rapid discovery: locate the most relevant paragraph(s) for a query and jump directly to the source page and context.
- Verifiable citations: return the original text snippet + page number so results are directly citable and avoid hallucination when used in downstream summaries.
- Reproducible ingestion: a Grobid-powered pipeline produces normalized snapshots (documents, headings, pages, texts) that can be re-run and audited.
- Semantic search over text chunks: embeddings are computed per chunk and stored in a vector index so similarity search returns focused text hits rather than whole-document matches.

The stack is designed for research and developer workflows where provenance, snippet-level precision, and low hallucination risk matter.

Getting started — dependencies & services
----------------------------------------

Recommended approach: run the supporting services (Grobid, Ollama embeddings) via Docker Compose included in the repository, then install the package in editable mode.

1. Start services (Grobid + Ollama):

```bash
docker-compose up -d
docker ps                       # confirm the dev container name (e.g., smartlib_dev)
docker exec -it smartlib_dev bash
```

2. Install package (editable) and Python deps:

```bash
python -m pip install -e .
python -m pip install -r requirements.txt
```

3. Verify services are healthy (tail logs as they start):

```bash
docker-compose logs -f grobid
docker-compose logs -f ollama
```

Notes:
- Grobid REST API: port `8070` (config: `smart_library.config.Grobid`).
- Ollama embedding endpoints: port `11434` (config: `smart_library.config.OllamaConfig`).
- The provided `docker-compose.yml` may include GPU/runtime options (e.g., `runtime: nvidia`) — remove or adjust if you don't have an NVIDIA runtime.

Quick CLI usage
---------------

Initialize the database schema (creates tables including `page_number` on text entities):

```bash
smartlib init
```

Ingest a PDF (creates document, pages, texts, and embeddings/vectors if configured):

```bash
smartlib add /path/to/your/file.pdf
```

Batch ingestion (optional)
--------------------------

If you want to ingest a whole folder of PDFs at once, run a simple shell loop from the repository root:

```bash
for f in data_dev/pdf/*.pdf; do smartlib add "$f"; done
```

Run a similarity search (top N results):

```bash
smartlib search "your query text" 5
```

List and inspect entities:

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

Programmatic scenario
---------------------

There is a programmatic scenario that exercises the CLI handlers (uses a temporary DB by default):

```bash
PYTHONPATH=src python3 src/smart_library/integration/scenarios/cli_workflow.py /path/to/your/file.pdf
```

Notes
-----

- Embeddings and Grobid extraction require the appropriate external services/configuration; if those are unavailable the pipeline will run partially and log errors.
- To preserve a temporary DB for inspection when running scenarios, use the `--keep-temp` flag on the scenario scripts.

Docker / Compose
-----------------

This repo includes a `docker-compose.yml` that brings up supporting services used by the ingestion
pipeline (Grobid for PDF extraction, Ollama for embeddings). For local development you can start
the required services with:

```bash
docker-compose up -d
```

Check logs while services start:

```bash
docker-compose logs -f grobid
docker-compose logs -f ollama
```

Notes:
- `grobid` exposes its REST API on port `8070` (configured in `smart_library.config.Grobid`).
- `ollama` exposes embedding and generation endpoints on port `11434` (configured in `smart_library.config.OllamaConfig`).
- The `docker-compose.yml` may reference GPU/runtime options (e.g., `runtime: nvidia`) — remove or
	adjust those if you do not have an NVIDIA runtime available on your machine.
- After the services are running, run `smartlib init` then `smartlib add /path/to/file.pdf` to ingest
	and create embeddings.

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
