"""SQLite-backed persistence for to-do items."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.models import Todo, TodoCreate, TodoUpdate

SCHEMA = """
CREATE TABLE IF NOT EXISTS todos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL,
    completed  INTEGER NOT NULL DEFAULT 0,
    created_at TEXT    NOT NULL
)
"""


class TodoStore:
    def __init__(self, db_path: str | Path) -> None:
        # check_same_thread=False: FastAPI may run sync handlers in a thread pool.
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def list(self) -> list[Todo]:
        rows = self._conn.execute("SELECT * FROM todos ORDER BY id").fetchall()
        return [_row_to_todo(row) for row in rows]

    def get(self, todo_id: int) -> Todo | None:
        row = self._conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        return _row_to_todo(row) if row else None

    def create(self, data: TodoCreate) -> Todo:
        created_at = datetime.now(UTC).isoformat()
        cursor = self._conn.execute(
            "INSERT INTO todos (title, completed, created_at) VALUES (?, 0, ?)",
            (data.title, created_at),
        )
        self._conn.commit()
        return self.get(cursor.lastrowid)

    def update(self, todo_id: int, data: TodoUpdate) -> Todo | None:
        existing = self.get(todo_id)
        if existing is None:
            return None
        title = data.title if data.title is not None else existing.title
        completed = data.completed if data.completed is not None else existing.completed
        self._conn.execute(
            "UPDATE todos SET title = ?, completed = ? WHERE id = ?",
            (title, int(completed), todo_id),
        )
        self._conn.commit()
        return self.get(todo_id)

    def delete(self, todo_id: int) -> bool:
        cursor = self._conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def clear_completed(self) -> int:
        cursor = self._conn.execute("DELETE FROM todos WHERE completed = 1")
        self._conn.commit()
        return cursor.rowcount


def _row_to_todo(row: sqlite3.Row) -> Todo:
    return Todo(
        id=row["id"],
        title=row["title"],
        completed=bool(row["completed"]),
        created_at=datetime.fromisoformat(row["created_at"]),
    )
