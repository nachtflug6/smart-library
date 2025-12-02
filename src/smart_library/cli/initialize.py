from typer import echo
from smart_library.cli.main import app

@app.command(name="init")
def initialize():
    """Initialize the database schema."""
    from smart_library.infrastructure.db.db import init_db
    try:
        init_db()
        echo("Database initialized successfully.")
    except Exception as e:
        echo(f"Error initializing database: {e}")