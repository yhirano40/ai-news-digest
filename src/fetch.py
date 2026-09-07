"""RSSフィードから当日分のAI関連記事候補を取得するモジュール。"""

from datetime import datetime, timedelta, timezone
from time import mktime

import feedparser

# サイトごとの取得設定。
# keyword_filter が None の場合はカテゴリRSS自体がAI専用なのでキーワード判定はしない。
# Ars TechnicaはAI専用カテゴリRSSがないため、キーワードで絞り込む。
FEEDS = [
    {
        "source": "TechCrunch",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "keyword_filter": None,
    },
    {
        "source": "The Verge",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "keyword_filter": None,
    },
    {
        "source": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "keyword_filter": [
            "ai", "artificial intelligence", "machine learning", "llm",
            "openai", "anthropic", "chatgpt", "gemini", "deepmind",
            "generative", "large language model", "neural network",
        ],
    },
]

MAX_PER_SOURCE = 3  # 1サイトあたりの最大掲載件数
LOOKBACK_HOURS = 36  # この時間内に公開された記事のみ対象（実行タイミングのブレを吸収）


def _matches_keywords(entry, keywords):
    if not keywords:
        return True
    tags = entry.get("tags", [])
    tag_text = " ".join(t.get("term", "") for t in tags if isinstance(t, dict))
    haystack = " ".join([entry.get("title", ""), entry.get("summary", ""), tag_text]).lower()
    return any(kw in haystack for kw in keywords)


def _published_datetime(entry):
    struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if not struct:
        return None
    return datetime.fromtimestamp(mktime(struct), tz=timezone.utc)


def fetch_all(seen_urls):
    """未処理・条件に合う記事候補を、サイトごとに新しい順で最大 MAX_PER_SOURCE 件ずつ集めて返す。"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    results = []

    for feed_cfg in FEEDS:
        parsed = feedparser.parse(feed_cfg["url"])
        picked = []

        for entry in parsed.entries:
            link = entry.get("link")
            if not link or link in seen_urls:
                continue
            if not _matches_keywords(entry, feed_cfg["keyword_filter"]):
                continue

            published_dt = _published_datetime(entry)
            if not published_dt or published_dt < cutoff:
                continue

            picked.append({
                "source": feed_cfg["source"],
                "title": entry.get("title", "(タイトルなし)"),
                "link": link,
                "published": published_dt.isoformat(),
                "rss_summary": entry.get("summary", ""),
            })

        picked.sort(key=lambda a: a["published"], reverse=True)
        results.extend(picked[:MAX_PER_SOURCE])

    return results
