import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(str(tmp_path / "test.db"))) as c:
        yield c


def test_list_starts_empty(client):
    assert client.get("/api/todos").json() == []


def test_create_todo(client):
    res = client.post("/api/todos", json={"title": "Ship it"})
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Ship it"
    assert body["completed"] is False
    assert client.get("/api/todos").json() == [body]


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_create_rejects_invalid_title(client, title):
    assert client.post("/api/todos", json={"title": title}).status_code == 422


def test_toggle_and_rename(client):
    todo_id = client.post("/api/todos", json={"title": "a"}).json()["id"]
    res = client.patch(f"/api/todos/{todo_id}", json={"completed": True})
    assert res.status_code == 200
    assert res.json()["completed"] is True
    res = client.patch(f"/api/todos/{todo_id}", json={"title": "b"})
    assert res.json() | {"created_at": None} == {
        "id": todo_id,
        "title": "b",
        "completed": True,
        "created_at": None,
    }


def test_update_missing_returns_404(client):
    assert client.patch("/api/todos/999", json={"completed": True}).status_code == 404


def test_delete(client):
    todo_id = client.post("/api/todos", json={"title": "a"}).json()["id"]
    assert client.delete(f"/api/todos/{todo_id}").status_code == 204
    assert client.delete(f"/api/todos/{todo_id}").status_code == 404


def test_clear_completed(client):
    done = client.post("/api/todos", json={"title": "done"}).json()["id"]
    client.post("/api/todos", json={"title": "open"})
    client.patch(f"/api/todos/{done}", json={"completed": True})
    res = client.delete("/api/todos/completed")
    assert res.json() == {"deleted": 1}
    assert [t["title"] for t in client.get("/api/todos").json()] == ["open"]


def test_data_persists_across_restarts(tmp_path):
    db = str(tmp_path / "persist.db")
    with TestClient(create_app(db)) as c:
        c.post("/api/todos", json={"title": "survive"})
    with TestClient(create_app(db)) as c:
        assert [t["title"] for t in c.get("/api/todos").json()] == ["survive"]


def test_serves_frontend(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert 'id="todo-list"' in res.text
    assert client.get("/app.js").status_code == 200
