"""記事URLから本文を抽出するモジュール。取得に失敗した場合はRSSの抜粋を使う。"""

import trafilatura


def extract_text(url, fallback=""):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text and len(text) > 200:
                return text
    except Exception:
        pass
    return fallback
