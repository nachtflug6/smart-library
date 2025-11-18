from typing import Any, Dict, Optional, TypeVar, Generic
import json
from smart_library.infrastructure.db import get_connection
from smart_library.domain.entities.entity import Entity

E = TypeVar("E", bound=Entity)


def _to_json(value):
    if value is None:
        return None
    return json.dumps(value)


def _from_json(value, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


class BaseRepository(Generic[E]):
    table: str  # child table
    columns: Dict[str, str]  # db_column -> entity_attribute
    json_columns: set[str] = set()  # db columns to JSON-encode
    join_entity: bool = True

    def __init__(self):
        self.conn = get_connection()

    # ---------- Base entity ----------
    def _insert_entity(self, e: Entity):
        sql = """
        INSERT INTO entity
        (id, created_at, modified_at, created_by, updated_by, parent_id, entity_kind, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(
            sql,
            [
                e.id,
                e.created_at,
                e.modified_at,
                e.created_by,
                e.updated_by,
                e.parent_id or None,
                e.__class__.__name__,
                _to_json(e.metadata),
            ],
        )

    def _update_entity_meta(self, e: Entity):
        sql = """
        UPDATE entity SET modified_at=?, updated_by=?, metadata=? WHERE id=?
        """
        self.conn.execute(
            sql,
            [e.modified_at, e.updated_by, _to_json(e.metadata), e.id],
        )

    def _delete_entity(self, entity_id: str):
        self.conn.execute("DELETE FROM entity WHERE id=?", (entity_id,))

    def _fetch_entity_row(self, entity_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM entity WHERE id=?", (entity_id,)).fetchone()
        return dict(row) if row else None

    # ---------- Base entity helpers ----------
    def _insert_entity_row(self, entity: Entity) -> None:
        sql = """
            INSERT INTO entity (id, created_at, modified_at, parent_id, type, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        metadata_json = json.dumps(getattr(entity, "metadata", {}) or {})
        values = [
            entity.id,
            entity.created_at,
            entity.modified_at,
            entity.parent_id or None,
            entity.__class__.__name__,  # Persist actual entity kind
            metadata_json,
        ]
        self.conn.execute(sql, values)

    def _delete_entity_row(self, entity_id: str) -> None:
        self.conn.execute("DELETE FROM entity WHERE id=?", (entity_id,))

    def _row_to_dict(self, row) -> Dict[str, Any]:
        return dict(row) if row is not None else {}

    # ---------- Child table generic ops ----------
    def add(self, entity: Entity) -> str:
        # Insert into base entity table first (FK will cascade)
        self._insert_entity_row(entity)

        # Prepare child insert
        db_cols = list(self.columns.keys())
        placeholders = ", ".join(["?"] * len(db_cols))
        sql = f"INSERT INTO {self.table} ({', '.join(db_cols)}) VALUES ({placeholders})"

        vals = []
        for col, attr in self.columns.items():
            val = getattr(entity, attr, None)
            if col in self.json_columns and val is not None:
                val = json.dumps(val)
            vals.append(val)

        self.conn.execute(sql, vals)
        self.conn.commit()
        return entity.id

    def get(self, entity_id: str) -> Optional[Dict[str, Any]]:
        # Optionally join with entity table to include base columns
        if self.join_entity:
            sql = f"""
                SELECT e.*, c.*
                FROM entity e
                JOIN {self.table} c ON c.id = e.id
                WHERE e.id=?
            """
        else:
            sql = f"SELECT * FROM {self.table} WHERE id=?"
        row = self.conn.execute(sql, (entity_id,)).fetchone()
        return self._row_to_dict(row) if row else None

    def delete(self, entity_id: str) -> None:
        # Deleting from entity cascades to child due to FK
        self._delete_entity_row(entity_id)
        self.conn.commit()
