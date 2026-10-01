# my-todo-app

A small to-do app: a FastAPI + SQLite backend serving a vanilla JavaScript frontend.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Running the app

```bash
uvicorn app.main:app --reload
```

Then open http://localhost:8000. To-dos are stored in `todos.db`; set
`TODO_DB_PATH` to use a different file.

## API

| Method   | Path                    | Description                      |
| -------- | ----------------------- | -------------------------------- |
| `GET`    | `/api/todos`            | List all to-dos                  |
| `POST`   | `/api/todos`            | Create a to-do (`{"title": ...}`) |
| `PATCH`  | `/api/todos/{id}`       | Update `title` and/or `completed` |
| `DELETE` | `/api/todos/{id}`       | Delete a to-do                   |
| `DELETE` | `/api/todos/completed`  | Delete all completed to-dos      |

Interactive docs are served at `/docs`.

## Checks

```bash
pytest
ruff check . && ruff format --check .
```
