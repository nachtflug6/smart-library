

import typer
import uuid
import numpy as np
from smart_library.domain.services.vector_service import VectorService

app = typer.Typer()

@app.command()
def random():
	"""
	Add a random vector (768-dim) to the database for testing sqlite-vec.
	Usage: smartlib add-vector random
	"""
	service = VectorService()
	vec = np.random.randn(768).astype(float).tolist()
	id = str(uuid.uuid4())
	model = "random-test"
	service.add_vector(id, vec, model)
	typer.echo(f"Random vector added: id={id}, model={model}")
