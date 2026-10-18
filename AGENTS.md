# AGENTS.md

このリポジトリでは、利用者に役立つ正確なゲーム情報と、保守しやすい公開サービスを優先する。

## 基本方針

- 公開ルール・評価・分析は、公式一次資料と本番データを根拠にする。
- 版・FAQ・エラッタの違いを混ぜない。根拠が不足する場合は推測で埋めず、未検証として扱う。
- silent fallback、根拠のない既定値、例外の握り潰しを追加しない。
- 新しい仕組みより既存実装と標準機能を優先し、不要なものは削除する。
- dead code、obsolete config、重複workflow、古い文書、個別ゲーム専用の一回限りの処理を残さない。

## ドキュメント

- 一般ドキュメントの置き場は `docs/` だけとする。
- `README.md` は利用者向けの入口、`AGENTS.md` は開発規約としてルートに残す。
- ツール固有の別ドキュメント置き場、archive、memory文書を作らない。
- 内容が重複する場合は新規追加ではなく、既存文書へ統合するか削除する。
- 公開Webサイトがある場合、`README.md` 冒頭にcanonical production URLを完全な `https://...` の平文で置く。

## 変更と検証

- 変更前に、現在のコード、Issue、Pull Request、CI、productionを確認する。
- test / data validation → Pull Request → exact-head CI → merge → main read-back → production verificationまで確認する。
- CI成功だけをproduction成功としない。
- 同じ問題が再発する場合は、その場の修正を繰り返さず、このファイル、CI、schema、testのうち最小の正規箇所へ再発防止を入れる。

## Outcome-first task interpretation (Altitude / Depth / Range / Speed)

- **Altitude:** Interpret a task as a verifiable user outcome, not only the named intermediate step. Infer the smallest justified acceptance criteria from the request and current repository state; do not silently expand scope or override explicit instructions.
- **Depth:** Use primary/current evidence and real domain tools and methods. Verify the actual postcondition independently of agent self-report, preferably on the exact changed revision or target runtime.
- **Range:** Combine code, data, tests, runtime/UI, and domain expertise when that materially improves the outcome, while respecting canonical owners and avoiding duplicate systems.
- **Speed:** Complete authorized read-only and reversible work through implementation, focused checks, and read-back without unnecessary approval loops. Bound retries and stop at the proven outcome.
- These principles never bypass repository-specific security, privacy, permission, publication, spending, destructive-action, or release boundaries. State verified results and any remaining `UNVERIFIED` layers.

## Compute-scaling adoption

Scale the search candidate count, local OSS retrieval/reranking model and explanation budget only after a frozen set of game-edition-specific queries demonstrates better answer quality. Measure edition/expansion/version correctness, cited official-source match, spoiler leakage, unsupported rule assertions, retrieval success, latency and memory on equal inputs. Treat deterministic card/rule validation and exact published corrections as authoritative, not LLM guesses. Preserve the current non-spoiler public surface and existing task/CI/Pages gates. Keep the low-compute baseline if higher budgets fail to improve measured accuracy.
