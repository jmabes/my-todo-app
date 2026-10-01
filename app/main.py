"""FastAPI application exposing a JSON API for to-do items."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles

from app.models import Todo, TodoCreate, TodoUpdate
from app.storage import TodoStore

DEFAULT_DB_PATH = "todos.db"
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def get_store(request: Request) -> TodoStore:
    return request.app.state.store


Store = Annotated[TodoStore, Depends(get_store)]

router = APIRouter(prefix="/api/todos", tags=["todos"])


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, "To-do not found")


@router.get("", response_model=list[Todo])
def list_todos(store: Store):
    return store.list()


@router.post("", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, store: Store):
    return store.create(data)


# Declared before /{todo_id} so "completed" is not parsed as an id.
@router.delete("/completed")
def clear_completed(store: Store):
    return {"deleted": store.clear_completed()}


@router.patch("/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, data: TodoUpdate, store: Store):
    todo = store.update(todo_id, data)
    if todo is None:
        raise _not_found()
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, store: Store):
    if not store.delete(todo_id):
        raise _not_found()


def create_app(db_path: str | None = None) -> FastAPI:
    db_path = db_path or os.environ.get("TODO_DB_PATH", DEFAULT_DB_PATH)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.store = TodoStore(db_path)
        yield
        app.state.store.close()

    app = FastAPI(title="To-do API", lifespan=lifespan)
    app.include_router(router)
    # Mounted last so /api routes take precedence over static files.
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
