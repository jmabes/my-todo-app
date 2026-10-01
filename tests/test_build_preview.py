import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "build_preview.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_preview", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preview_is_self_contained():
    html = load_builder().build()
    assert "<title>My To-Do App</title>" in html
    assert 'id="todo-list"' in html
    # Uses the browser-storage API, never the HTTP client or external files.
    assert "localStorage" in html
    assert "api/todos" not in html
    assert 'src="' not in html
    assert 'href="styles.css"' not in html
