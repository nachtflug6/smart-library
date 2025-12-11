from typer import Argument, Option, echo
from smart_library.infrastructure.db.db import check_sqlitevec_index, get_connection_with_sqlitevec
from smart_library.cli.main import app

@app.command(name="test-sqlitevec")
def test_sqlitevec(
  table_name: str = Argument("vector", help="Name of the vector table to check (default: vector)"),
  test_similarity: bool = Option(False, "--test-similarity", help="Test vector similarity functions (sqlite-vec)")
):
    """
    Test sqlite-vec extension and vector table health.
    Usage:
      smartlib test-sqlitevec [table_name]
    """
    result = check_sqlitevec_index(table_name=table_name)
    echo(result)
    if test_similarity:
      echo("\nTesting vector similarity functions using sqlite-vec functions:")
      conn = get_connection_with_sqlitevec(load_sqlitevec=True)
      cur = conn.cursor()
      # Insert three test vectors into the table using correct schema
      vectors = {
        "v1": [1.0, 0.0, 0.0],
        "v2": [0.0, 1.0, 0.0],
        "v3": [1.0, 1.0, 0.0],
      }
      # Clean up any previous test rows
      for k in vectors:
        cur.execute(f"DELETE FROM {table_name} WHERE id = ?", (k,))
      conn.commit()
      # Insert vectors as multiple rows (id, idx, value, model, dim)
      import numpy as np
      def normalize(vec):
        v = np.array(vec, dtype=float)
        return (v / np.linalg.norm(v)).tolist()
      for k, v in vectors.items():
        vec_norm = normalize(v)
        for idx, value in enumerate(vec_norm):
          cur.execute(f"INSERT INTO {table_name}(id, idx, value, model, dim) VALUES (?, ?, ?, ?, ?)", (k, idx, float(value), "test", 3))
      conn.commit()
      # Test similarity using sqlite-vec functions
      for a, b, name in [ ("v1", "v2", "v1 vs v2"), ("v1", "v3", "v1 vs v3"), ("v2", "v3", "v2 vs v3") ]:
        a_vec = normalize(vectors[a])
        b_vec = normalize(vectors[b])
        a_str = ",".join(str(x) for x in a_vec)
        b_str = ",".join(str(x) for x in b_vec)
        try:
          cosine = cur.execute("SELECT vec_cosine(vec_from_list(?), vec_from_list(?))", (a_str, b_str)).fetchone()[0]
          l2 = cur.execute("SELECT vec_l2(vec_from_list(?), vec_from_list(?))", (a_str, b_str)).fetchone()[0]
          dot = cur.execute("SELECT vec_dot(vec_from_list(?), vec_from_list(?))", (a_str, b_str)).fetchone()[0]
          echo(f"{name}: cosine={cosine}, l2={l2}, dot={dot}")
        except Exception as e:
          echo(f"{name}: ERROR: {e}")
      # Clean up test rows
      for k in vectors:
        cur.execute(f"DELETE FROM {table_name} WHERE id = ?", (k,))
      conn.commit()
      conn.close()

if __name__ == "__main__":
    app()
