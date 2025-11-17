from typer import Typer, Option, echo

app = Typer(no_args_is_help=True)

@app.command("db-init")
def db_init():
    """Initialize Database."""
    from smart_library.infrastructure.db.init_db import init_db
    init_db()

@app.command("import-documents")
def import_documents_cmd():
    """Import Documents."""
    from smart_library.infrastructure.db.import_entities import import_documents
    import_documents()

@app.command("import-pages")
def import_pages_cmd():
    """Import Pages."""
    from smart_library.infrastructure.db.import_entities import import_pages
    import_pages()

@app.command("import-entities")
def import_entities_cmd():
    """Import all Entities (Documents + Pages)."""
    from smart_library.infrastructure.db.import_entities import import_entities
    import_entities()


@app.command("db-check")
def db_check():
    """Check DB consistency and file links."""
    from smart_library.infrastructure.db.check_db import check_db
    print(check_db())

@app.command("view")
def view_cmd(document_id: str, page: int):
    """View the text of a specific page."""
    from smart_library.infrastructure.db.view import view_page
    view_page(document_id, page)

@app.command("search")
def search_cmd(query: str):
    """Search for text inside all pages."""
    from smart_library.infrastructure.db.search import search
    search(query)


if __name__ == "__main__":
    app()