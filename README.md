# smart-library

Minimal quickstart
------------------

Installation (editable / development):

```bash
python -m pip install -e .
python -m pip install -r requirements.txt
```

This installs the package in editable mode so the `smartlib` console entry point becomes available locally.

Basic CLI usage
---------------

Initialize the database schema:

```bash
smartlib init
```

Ingest a PDF (creates document, pages, texts, and embeddings/vectors if configured):

```bash
smartlib add /path/to/your/file.pdf
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
