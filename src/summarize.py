"""Claude APIで記事を日本語要約するモジュール。"""

import json
import re

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """あなたはテクノロジー/AI分野のニュース編集者です。
与えられた英語記事の情報をもとに、日本語で読者向けの要約を作成してください。

出力は必ず次のキーを持つJSONオブジェクトのみとし、それ以外の文章（前置き・コードフェンスなど）は一切含めないでください。

{
  "title_ja": "記事タイトルの日本語訳（意訳可、30〜40文字程度）",
  "overview": "何が起きたかの概要（1〜2文）",
  "background": "背景・経緯（1〜2文）",
  "points": ["技術的/ビジネス的なポイントを1項目ずつ書いた配列。2〜3項目程度"],
  "importance": "この出来事が重要な理由・今後への影響（1〜2文）"
}

全体として5〜8行程度の分量になるよう、簡潔かつ具体的に書いてください。数字や固有名詞は原文から正確に拾ってください。"""


def _parse_json(raw):
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def summarize_article(client, source, title, url, published, text):
    user_prompt = f"""以下は{source}に掲載された記事です。

タイトル: {title}
URL: {url}
掲載日時: {published}

本文（取得できた範囲。抜粋の場合あり）:
{text[:6000]}

上記を踏まえて、指定のJSON形式で日本語要約を作成してください。"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw_text = response.content[0].text
    return _parse_json(raw_text)
