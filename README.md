# AIニュース ダイジェスト

TechCrunch・The Verge・Ars Technica のAI関連記事を毎日自動収集し、Claude（Sonnet 5）で日本語要約して静的ページに公開するツールです。

## 仕組み

1. GitHub Actions が毎朝（JST 8:00）起動
2. 各サイトのRSSからAI関連の新着記事を取得（各サイト上位2〜3件、合計5〜8件目安）
3. 記事本文を取得し、Claude APIで日本語要約（概要・背景・ポイント・重要性の構成）
4. `docs/` 以下に静的HTMLを生成し、GitHub Pagesで公開
5. `data/archive/` に日付ごとの要約データを保存し、過去分は `docs/archive/` から閲覧可能

## ディレクトリ構成

```
.github/workflows/daily.yml   毎日の自動実行ワークフロー
src/                          パイプライン本体（取得・抽出・要約・ページ生成）
templates/                    Jinja2テンプレート
data/                         取得済みURL・日別の生データ/要約（JSON）
docs/                         GitHub Pagesで公開する静的ページ
```

## ローカルでの試し方

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
# .env を開き、ANTHROPIC_API_KEY に自分のAPIキーを設定

python -m src.main
```

実行後、`docs/index.html` をブラウザで開くと結果を確認できます。

## GitHubで自動運行させる手順

1. GitHub上で空のリポジトリを作成し、このフォルダをpush
   ```bash
   git remote add origin <あなたのリポジトリURL>
   git push -u origin main
   ```
2. リポジトリの **Settings > Secrets and variables > Actions** で `ANTHROPIC_API_KEY` を登録
3. **Settings > Pages** で Source を「Deploy from a branch」、Branch を `main` / `/docs` に設定
4. **Actions** タブから `Daily AI News Digest` を選び、`Run workflow` で初回を手動実行
5. 以降は毎日自動更新されます（スケジュールは `.github/workflows/daily.yml` の `cron` で変更可能）

## 注意事項

- 生成ページには要約とリンクのみを掲載し、原文全文は転載しない設計にしています（著作権配慮）。
- 各サイトの利用規約・robots.txtは変更される可能性があるため、公開範囲を広げる前に定期的に確認してください。
- Ars TechnicaはAI専用のRSSがないため、記事のタイトル・要約・タグに含まれるキーワードでAI関連記事を判定しています（`src/fetch.py` の `keyword_filter` で調整可能）。
