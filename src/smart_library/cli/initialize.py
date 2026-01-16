from typer import echo
from smart_library.cli.main import app

@app.command(name="init")
def initialize():
    """Initialize the database schema and clean PDF storage."""
    from smart_library.infrastructure.db.db import init_db
    from smart_library.config import DOC_PDF_DIR
    import shutil
    from pathlib import Path
    
    try:
        # Initialize database
        init_db()
        echo("Database initialized successfully.")
        
        # Clean PDF directory
        if DOC_PDF_DIR.exists():
            shutil.rmtree(DOC_PDF_DIR)
            echo(f"Cleaned PDF directory: {DOC_PDF_DIR}")
        
        # Recreate empty PDF directory
        DOC_PDF_DIR.mkdir(parents=True, exist_ok=True)
        echo("PDF storage directory ready.")
        
        # Reset search session
        session_file = Path.cwd() / ".search_session.json"
        if session_file.exists():
            session_file.unlink()
            echo("Search session reset.")
        
    except Exception as e:
        echo(f"Error during initialization: {e}")