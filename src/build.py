"""要約済みデータからHTMLページ（当日ページ・アーカイブ）を生成するモジュール。"""

import json
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
DATA_ARCHIVE = ROOT / "data" / "archive"
DOCS = ROOT / "docs"
DOCS_ARCHIVE = DOCS / "archive"
TEMPLATES = ROOT / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html"]),
)


def _load_all_days():
    days = []
    for path in sorted(DATA_ARCHIVE.glob("*.json"), reverse=True):
        days.append(json.loads(path.read_text(encoding="utf-8")))
    return days


def build_site():
    DOCS.mkdir(exist_ok=True)
    DOCS_ARCHIVE.mkdir(parents=True, exist_ok=True)

    days = _load_all_days()
    if not days:
        return

    latest = days[0]
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    index_template = env.get_template("index.html.j2")
    day_template = env.get_template("day.html.j2")
    archive_index_template = env.get_template("archive_index.html.j2")

    (DOCS / "index.html").write_text(
        index_template.render(day=latest, generated_at=generated_at),
        encoding="utf-8",
    )

    for day in days:
        (DOCS_ARCHIVE / f"{day['date']}.html").write_text(
            day_template.render(day=day, generated_at=generated_at),
            encoding="utf-8",
        )

    (DOCS_ARCHIVE / "index.html").write_text(
        archive_index_template.render(days=days, generated_at=generated_at),
        encoding="utf-8",
    )
