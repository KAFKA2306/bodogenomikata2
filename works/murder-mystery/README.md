# オリジナル・マーダーミステリー制作

ここは、既存作品の調査データではなく、**人間が発案し、人間が最終判断する新作**を置く場所です。

## まず開く場所

```text
works/murder-mystery/projects/{slug}/private/WORK.md
```

普段の制作では、この`WORK.md`だけを開けば足ります。人物、起承転結、謎、驚き、感情、結末、未決事項を一枚にまとめます。

## 構造

```text
works/murder-mystery/
├── README.md
├── index.yaml
├── projects/
│   └── {slug}/
│       ├── project.yaml       # 状態、所有者、次の行動、制作来歴
│       ├── README.md          # 入口と公開説明
│       └── private/           # 犯人、真相、HO、結末、プレイテスト資料
└── _template/                 # 新規作品用テンプレート
```

作品の進行状態が変わってもディレクトリは移動しません。`project.yaml`の`status`だけを更新します。

## 状態

- `seed` — 原初の観察、執着、問いを記録した段階
- `developing` — 人物、因果、起承転結、驚き、感情を接続中
- `playtesting` — 実際のプレイヤー反応で仮説を検証中
- `production` — 頒布版、素材、運用を固定中
- `archived` — 凍結、破棄、他作品へ統合済み

状態は検索・一覧表示のためのラベルであり、作品ファイルを分散させる理由にはしません。

## 新規作品

```bash
task work:new -- my-work "仮タイトル"
```

生成後は`private/WORK.md`を人間が先に書きます。

## 人間主体の規則

人間が決めるもの:

- 最初の観察、記憶、違和感、執着
- 倫理的矛盾
- 人物の人生、欲求、依存、加害
- 真相と因果
- 中心となる驚き
- クライマックスの選択
- 結末
- 最終的な台詞と文章

AIを補助に限定できるもの:

- メモの整理
- 矛盾や不足の指摘
- 調査補助と出典管理
- 比較表やチェックリスト
- プレイテスト記録の要約

`canonicalPlotGeneratedByAI: false`を構造検証で強制します。AI支援プロトタイプは、`prototypeGeneratedWithAI: true`として制作来歴を明記し、人間作の正準版と区別します。

## ネタバレ資料の追跡

`private/`は既定でGit追跡しません。ただし、所有者が公開管理を明示的に承認した作品だけ、作品単位で追跡できます。

必要条件:

```yaml
privacy:
  trackedSpoilers: true
  spoilerMaterialTrackedInThisRepository: true
  publicationApprovedByOwner: true
```

さらに`.gitignore`へ、その作品だけを対象にした例外を追加します。別作品の`private/`が誤って追跡された場合、`task work:validate`は失敗します。

現在の公開ネタバレ作品:

- `projects/unanimous-kindness/` — 『満場一致で、あなたをやめる』Prototype 0.4

## 検証

```bash
task work:validate
```

検証対象:

- 全作品が`projects/{slug}`の固定パスにある
- statusが統制語彙内である
- 正準プロットのAI生成を許可していない
- ネタバレ追跡は所有者承認済み作品だけである
- 旧工程ディレクトリと分割テンプレートが復活していない
