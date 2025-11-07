from typer import Typer

app = Typer()

@app.command("db-init")
def db_init():
    from smart_library.db.init_db import init_db
    init_db()

@app.command("import-pages")
def import_pages_cmd():
    from smart_library.db.import_entities import import_pages
    import_pages()

if __name__ == "__main__":
    app()