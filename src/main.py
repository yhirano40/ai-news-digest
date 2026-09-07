"""パイプライン全体（取得→抽出→要約→保存→ページ生成）を実行するエントリーポイント。"""

import json
import os
from datetime import date
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from src import fetch, extract, summarize, build

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ARCHIVE_DIR = DATA_DIR / "archive"
SEEN_PATH = DATA_DIR / "seen_urls.json"


def load_seen():
    if SEEN_PATH.exists():
        return set(json.loads(SEEN_PATH.read_text(encoding="utf-8")))
    return set()


def save_seen(seen):
    SEEN_PATH.write_text(
        json.dumps(sorted(seen), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY が設定されていません（.env または環境変数を確認してください）")

    client = Anthropic(api_key=api_key)
    seen = load_seen()

    candidates = fetch.fetch_all(seen)
    if not candidates:
        print("新しい対象記事が見つかりませんでした。ページは更新しません。")
        return

    articles = []
    for item in candidates:
        text = extract.extract_text(item["link"], fallback=item["rss_summary"])
        try:
            item_summary = summarize.summarize_article(
                client, item["source"], item["title"], item["link"], item["published"], text
            )
        except Exception as e:
            print(f"要約に失敗しました: {item['link']} ({e})")
            continue

        articles.append({**item, "summary": item_summary})
        seen.add(item["link"])

    if not articles:
        print("要約できた記事がありませんでした。ページは更新しません。")
        return

    today = date.today().isoformat()
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ARCHIVE_DIR / f"{today}.json"

    # 同日に複数回実行された場合は既存分に追記する
    if out_path.exists():
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        existing_links = {a["link"] for a in existing["articles"]}
        articles = existing["articles"] + [a for a in articles if a["link"] not in existing_links]

    out_path.write_text(
        json.dumps({"date": today, "articles": articles}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    save_seen(seen)
    build.build_site()
    print(f"{len(articles)}件の記事を{today}のページに反映しました。")


if __name__ == "__main__":
    main()
