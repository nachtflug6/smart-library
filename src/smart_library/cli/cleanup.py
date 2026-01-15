"""CLI command to clean up orphaned vectors."""
from typer import Typer
from smart_library.cli.main import app
from smart_library.infrastructure.repositories.vector_repository import VectorRepository

cleanup_app = Typer(help="Clean up orphaned vectors")
app.add_typer(cleanup_app, name="cleanup")


@cleanup_app.command("vectors")
def cleanup_vectors():
    """
    Remove orphaned vectors that have no corresponding text entities.
    
    This can happen if vectors were created before the deletion fix was in place.
    Run this command if you see ghost search results after deleting documents.
    """
    try:
        repo = VectorRepository.default_instance()
        deleted_count = repo.cleanup_orphaned_vectors()
        
        if deleted_count > 0:
            print(f"✓ Cleaned up {deleted_count} orphaned vector(s)")
        else:
            print("✓ No orphaned vectors found - database is clean")
        
        return 0
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
