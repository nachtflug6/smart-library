from typer import Typer

app = Typer()

@app.command("db-init")
def db_init():
    from smart_library.db.init_db import init_db
    init_db()

@app.command("import-documents")
def import_documents_cmd():
    """Import Documents."""
    from smart_library.db.import_entities import import_documents
    import_documents()

@app.command("import-pages")
def import_pages_cmd():
    """Import Pages."""
    from smart_library.db.import_entities import import_pages
    import_pages()

@app.command("db-check")
def db_check():
    """Check DB consistency and file links."""
    from smart_library.db.check_db import check_db
    print(check_db())


if __name__ == "__main__":
    app()