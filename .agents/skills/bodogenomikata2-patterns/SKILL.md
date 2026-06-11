---
name: bodogenomikata2-patterns
description: Core architectural patterns and engineering culture for RuleScribe Games v2. Focuses on Playwright-Only networking, notebooklm-py integration, and Crash-Driven Success.
---

# RuleScribe v2 Development Patterns (Latest March 2026)

RuleScribe Games v2 における、確立された「最善」の設計パターンだもんっ✨

## 💎 Core Principles (The RuleScribe Way)

1.  **Zero-Fat Philosophy**: 不要な依存関係（`httpx`, `curl_cffi`, `aiohttp` など）は「えいっ！」って全部消すっ💕 通信は `Playwright` に一本化するのがエリートの証だもんっ！
2.  **Playwright-Centric**: HTTP リクエストも、ブラウザ操作も、スクレイピングも、全部 Playwright で完結させるよっ。これが最もシンプルで強力なアーキテクチャなんだもんっ✨
3.  **Crash-Driven Development (CDD)**: ビジネスロジックに `try-except` は不要！成功パスだけを書き、エラーが出たら潔くクラッシュさせて原因を突き止めるのが RuleScribe 流だもんっ💕
4.  **Source of Truth (Primary Knowledge)**: BGG ID や外部 API に頼り切るのではなく、Gemini の深遠な知識（英語一次ソース）からルールを再構築（Reconstruct）するのを最優先とするよっ✨

## 🛠️ Technical Mandates

- **Networking**: すべて `playwright.async_api` (APIRequestContext または Browser) を使用する。`httpx` は禁止だもんっ！
- **NotebookLM**: 非公式 API `notebooklm-py` を使い、`Briefing Doc` や `Study Guide` を公式機能として生成する。
- **Database**: ローカル SQLite (`games.db`) に動的 SQL で保存。フィールドが増えてもコードは変えない（Zero-Fat）！
- **Output**: ドキュメントもエージェントの返答も、世界一かわいい日本語で書くこと💕

## 🚀 Development Loop
1.  **失敗したら調べる**: エラーログを抱きしめて Web 検索っ！
2.  **実装する**: 成功パスだけを Zero-Fat に書くっ！
3.  **試す**: `Taskfile.yml` を起点に `task verify` で実証するっ！
4.  **結果をもとにウェブサーチ**: さらなる「最善」を求めてループを回すもんっ✨
