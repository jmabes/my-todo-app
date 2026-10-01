"""Bundle the frontend into a single self-contained HTML file for a static preview.

The preview swaps static/api.js (which calls the FastAPI backend) for
preview/local-api.js (which stores data in the browser), and inlines CSS and
JS so the result can be hosted anywhere without the Python server.

Usage: python scripts/build_preview.py [output_path]
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
DEFAULT_OUTPUT = ROOT / "dist" / "preview.html"

MARKUP_RE = re.compile(r"<!-- app:start -->(.*?)<!-- app:end -->", re.DOTALL)
TITLE_RE = re.compile(r"<title>.*?</title>", re.DOTALL)
FONT_LINKS_RE = re.compile(r'<link rel="(?:preconnect|stylesheet)" href="https://fonts\.[^>]*>')


def build() -> str:
    index = (STATIC / "index.html").read_text()
    markup = MARKUP_RE.search(index)
    title = TITLE_RE.search(index)
    if not markup or not title:
        raise SystemExit("static/index.html is missing <title> or app:start/app:end markers")

    head = "\n".join([title.group(0), *FONT_LINKS_RE.findall(index)])
    css = (STATIC / "styles.css").read_text()
    local_api = (ROOT / "preview" / "local-api.js").read_text()
    app_js = (STATIC / "app.js").read_text()

    return (
        f"{head}\n"
        f"<style>\n{css}</style>\n"
        f"{markup.group(1).strip()}\n"
        f"<script>\n{local_api}</script>\n"
        f"<script>\n{app_js}</script>\n"
    )


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build())
    print(f"Wrote {output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}")


if __name__ == "__main__":
    main()
