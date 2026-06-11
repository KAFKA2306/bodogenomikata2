# 🤖 NotebookLM v2 Workflow Guide

RuleScribe Games v2 の核心である NotebookLM を使用した「最強のルール解析」ワークフローです✨
必ず毎回まずweb検索する
## 🚀 成功パス (The Success Path)

1.  **PDF 準備**: `assets/pdfs/{game_slug}.pdf` に公式ルールを配置します。
2.  **自動解析実行**:
    ```bash
    PYTHONPATH=backend uv run scripts/notebooklm_auto.py --input assets/pdfs/catan.pdf
    ```
3.  **成果物の確認**:
    *   `backend/games.db`: 解析された構造化データが SQLite に保存されます。
    *   `assets/generated/`: スライド原稿やサマリーが生成されます。

## 🏛️ v2 アーキテクチャの規律

- **Playwright Only**: ブラウザ操作はすべて Playwright で完結し、最高精度の自動化を実現します。
- **Japanese First**: NotebookLM への指示および出力は、すべて「わかりやすい日本語」を基準とします。
- **Local Persistence**: 解析結果は即座にローカル SQLite に `upsert` され、API 経由で即時閲覧可能になります。

## 🕵️ トラブルシューティング（Crash-Driven）

- **ログイン要求**: 初回実行時やセッション切れの際は、Playwright がクラッシュするか、認証画面で停止します。その場合は `open_browser.py`（必要に応じて再構築）で手動ログインを行ってください。
- **タイムアウト**: PDF が巨大な場合は `NOTEBOOKLM_TIMEOUT_STRATEGY.md` を参照して設定を調整してください。

---
**Everything is grounded in reality. Use the truth of PDF.**
