---
name: ecc-zero-fat
description: 贅肉を削ぎ落とし、筋肉質なコードベースを作る知能。不要な依存関係（httpx等）の排除、防御的プログラムの全削除、成功パスのみの記述を徹底。
---

# ECC Zero-Fat Skill (Latest March 2026)

RuleScribe Games の美しさを支える「贅肉排除」の精神だもんっ✨

## 💎 Zero-Fat Mandates (RuleScribe v2 Edition)

1.  **Kill Redundant Clients**: `httpx`, `requests`, `aiohttp`, `curl_cffi`……全部いらないっ💕 Playwright 一本化によって、依存関係の 80% を削減するもんっ！
2.  **Delete Defensive Code**: `if x is not None` や `try-except` は「脂肪」だもんっ！成功パスだけを堂々と書き、失敗は CDD (Crash-Driven) で潔く受け入れる。
3.  **No Manual Mappings**: DB カラムを Python コードに書き並べるのは Fat だね。動的 SQL を使い、スキーマの変更に自動で追従させるっ✨
4.  **Self-Documenting Code**: 長いコメントやドキュメントは「脂肪」になりやすい。説明しなくてもわかる、美しく語るような命名を心がけるよっ💕

## 🛠️ Implementation Patterns
- **API**: `request_context` だけで完結させる。
- **DB**: `dict.keys()` からクエリを自動生成。
- **Logic**: 異常系はフレームワーク（FastAPI）に丸投げする。

筋肉質なコードこそが、最高速の知性を生むんだもんっ✨💕
