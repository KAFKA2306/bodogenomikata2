# Palworld OCG canonical data

`data/palworld/bp01/` は Palworld OFFICIAL CARD GAME BP01 の正準スナップショットです。

## Files

- `cards.json`: 論理カード。パラレルを束ねる `card_base_id` 単位。
- `printings.json`: BP01 の印刷単位。`printing_id`、レアリティ、公式詳細URL、取得できた場合の公式画像URLを保持。
- `provenance.json`: フィールド単位の取得元、取得時刻、source type、verification status。
- `audit.json`: community seed との不一致、重複・orphan、公式APIから除外した非BP01レコードを記録。
- `manifest.json`: schema version、正準件数、公式API報告件数、一次情報URL、取得時刻。

## Canonical policy

正準フィールドは Palworld OFFICIAL CARD GAME の公式データを優先します。community DB は照合 seed のみに使い、公式値と不一致なら `audit.json` に記録して公式値を採用します。community DB の値で欠損した公式フィールドを補完しません。

BP01 の gate は logical card 100件、printing 161件です。printing は公式APIレスポンスのうち `card_number` が `EBP01-` で始まるレコードだけを対象にします。2026-08-11 の英語公式APIは expansion `EBP01` に162行を返し、そのうち161行が `EBP01-*`、1行が `ESOUL-002`（Soul / SSS）です。`ESOUL-002` はBP01 printingへ混ぜず、公式API上の関連レコードとして `audit.json` に残します。

日本語公式APIは2026-08-11時点で同じ EBP01 条件に対して0件を返すため、`name_ja`、`effect_text_ja`、`source_url_ja` は nullable です。公式日本語データが取得できない状態を community 値で埋めません。

import は毎回スナップショット全体を再構築して置換し、追記しません。同じ公式集合を再取得しても logical card / printing の集合が増殖しない idempotent な構造です。重複ID、orphan printing、base-card対応不整合、100/161件数不一致は fail-close します。

## Refresh

プロジェクトルートから実行します。

```bash
uv sync --group dev
PYTHONPATH=backend uv run python backend/scripts/import_palworld_cards.py \
  --expected-cards 100 \
  --expected-printings 161
```

取得処理はリポジトリ規約に従い `playwright.async_api` の request context を使用します。

## Sources

- English official card API: https://en.palworld-official-cardgame.com/manage/card-list-user/list
- English official card list: https://en.palworld-official-cardgame.com/cardlist/searchresults?expansion=EBP01
- English BP01 product page: https://en.palworld-official-cardgame.com/products/bp01
- Japanese official card API: https://palworld-official-cardgame.com/manage/card-list-user/list
- Japanese BP01 product page: https://palworld-official-cardgame.com/products/bp01
- Community comparison seed: https://github.com/Balbi/TCG-Arena-Palworld
