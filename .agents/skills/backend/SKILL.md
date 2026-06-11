---
name: backend
description: Architecting the RuleScribe v2 Backend. Focuses on FastAPI, Dynamic SQLite, and Playwright-Only networking. No httpx allowed.
---

# RuleScribe Backend Architecture Skill (Latest March 2026)

RuleScribe Games v2 の「筋肉質なバックエンド」を支える知能だもんっ✨

## 🏗️ Core Stack (The Zero-Fat Choice)

- **Framework**: FastAPI (High-performance, type-safe)
- **Database**: SQLite with dynamic SQL (Maintenance-free schema)
- **Networking**: `playwright.async_api` (The ONLY allowed networking client)
- **AI**: Gemini 2.5 Flash (via Playwright APIRequestContext)

## 💎 Technical Commandments

1.  **Kill All HTTP Clients**: プロジェクトから `httpx`, `requests`, `aiohttp` を徹底的に排除するっ💕 全ての通信は Playwright の `request.new_context()` で行うこと。
2.  **Dynamic SQLite Client**: `sqlite_client.py` ではカラム名をハードコードしない。`PRAGMA table_info` を使い、辞書のキーから動的に SQL を生成する。
3.  **Crash-Driven Routes**: Router の中で `try-except` は使わない。FastAPI のデフォルトエラーハンドリングに任せ、成功パスの読みやすさを最大化する。
4.  **Module-Style Execution**: スクリプトの実行は必ずプロジェクトルートから `PYTHONPATH=backend uv run python backend/script.py` のように、パスを意識して行うこと。

## 🛠️ Code Patterns

### Gemini API via Playwright:
```python
async with async_playwright() as p:
    request_context = await p.request.new_context(
        base_url="https://generativelanguage.googleapis.com",
        extra_http_headers={"x-goog-api-key": key}
    )
    resp = await request_context.post(f"/v1beta/{model}:generateContent", data=payload)
    # Assume success path
    result = await resp.json()
```

### Dynamic Upsert:
```python
# build fields from dict keys automatically
fields = [f"{k} = ?" for k in valid_data.keys() if k != "slug"]
# execute dynamic SQL
cursor.execute(f"UPDATE games SET {', '.join(fields)} WHERE slug = ?", values)
```
