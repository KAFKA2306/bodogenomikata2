---
name: ecc-search-first
description: 「コードを書く前に、まず調べるっ！」が合言葉。失敗から得た証拠（401エラー等）をもとに、最短距離の解決策（Playwright/API連携）を導き出す知能。
---

# ECC Search-First Skill (Latest March 2026)

RuleScribe Games の開発において、最も重要な「調査第一」の精神だもんっ✨

## 💎 The Evidence-Based Loop
1.  **失敗を抱きしめる**: `401 Unauthorized` や `ModuleNotFoundError` が出たらチャンスっ！エラーメッセージをそのまま Web 検索に投げるよっ💕
2.  **多角的リサーチ**: 1つのクエリで諦めないっ！3〜5つのバリエーション（公式ドキュメント、GitHub Issue、最新技術ブログ）で深掘りするもんっ✨
3.  **実機調査 (Inspect)**: 外部ドキュメントが古ければ、`dir()` や `inspect.signature()` でコードの中にある「生の真実」を暴き出すっ💕
4.  **結果をもとにピボット**: 脆弱な API を捨てて堅牢なスクレイピングに、あるいは重いブラウザを捨てて高速な内部 API に、証拠に基づいて大胆に方向転換するよっ✨

## 🛠️ Search Guidelines for 2026
- **Google Search**: `site:boardgamegeek.com` のように範囲を絞って最新情報を狙い撃つ。
- **Library Internals**: ドキュメントのない非公式ライブラリ（`notebooklm-py`等）は、ソースコードそのものを「Source of Truth」として読み解く。
- **Reproducibility**: 「なんとなく動いた」は NG。なぜ動いたのか、エビデンス（実証データ）を必ずドキュメントに残すこと。
