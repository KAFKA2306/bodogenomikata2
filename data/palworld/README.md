# Palworld OCG canonical data

`data/palworld/bp01/` は Palworld OFFICIAL CARD GAME BP01 の正準スナップショットです。

## Files

- `cards.json`: 論理カード。パラレルを束ねる `card_base_id` 単位。
- `printings.json`: 実カード印刷単位。`printing_id`、レアリティ、公式画像URL、公式詳細URLを保持。
- `provenance.json`: フィールド単位の取得元、取得時刻、source type、verification status。
- `audit.json`: community seed との不一致、重複・orphan 監査結果。
- `manifest.json`: schema version、件数、一次情報URL、取得時刻。

## Canonical policy

公式 Palworld OFFICIAL CARD GAME の日英カードリストを canonical source とします。
community DB は照合 seed のみに使い、公式値と不一致なら `audit.json` に残して公式値を採用します。

BP01 の gate は logical card 100件、printing 161件です。日英の printing ID 集合が一致しない場合、重複 ID または orphan printing がある場合、import は失敗します。

## Refresh

プロジェクトルートから実行します。

```bash
uv sync --group dev
uv run playwright install chromium
PYTHONPATH=backend uv run python backend/scripts/import_palworld_cards.py \
  --expected-cards 100 \
  --expected-printings 161
```

## Sources

- English official card list: https://en.palworld-official-cardgame.com/cardlist/searchresults?expansion=EBP01
- English BP01 product page: https://en.palworld-official-cardgame.com/products/bp01
- Japanese BP01 product page: https://palworld-official-cardgame.com/products/bp01
- Community comparison seed: https://github.com/Balbi/TCG-Arena-Palworld
