import pytest
from pydantic import ValidationError

from app.models import TodoCreate, TodoUpdate
from app.storage import TodoStore


@pytest.fixture
def store():
    s = TodoStore(":memory:")
    yield s
    s.close()


def test_create_and_list(store):
    todo = store.create(TodoCreate(title="  Buy milk  "))
    assert todo.id == 1
    assert todo.title == "Buy milk"
    assert todo.completed is False
    assert store.list() == [todo]


def test_whitespace_only_title_rejected():
    with pytest.raises(ValidationError):
        TodoCreate(title="   ")


def test_get_missing_returns_none(store):
    assert store.get(42) is None


def test_update_partial_fields(store):
    todo = store.create(TodoCreate(title="Write tests"))
    updated = store.update(todo.id, TodoUpdate(completed=True))
    assert updated.completed is True
    assert updated.title == "Write tests"

    renamed = store.update(todo.id, TodoUpdate(title="Write more tests"))
    assert renamed.title == "Write more tests"
    assert renamed.completed is True


def test_update_missing_returns_none(store):
    assert store.update(99, TodoUpdate(completed=True)) is None


def test_delete(store):
    todo = store.create(TodoCreate(title="Temp"))
    assert store.delete(todo.id) is True
    assert store.delete(todo.id) is False
    assert store.list() == []


def test_clear_completed(store):
    a = store.create(TodoCreate(title="a"))
    store.create(TodoCreate(title="b"))
    store.update(a.id, TodoUpdate(completed=True))
    assert store.clear_completed() == 1
    assert [t.title for t in store.list()] == ["b"]
