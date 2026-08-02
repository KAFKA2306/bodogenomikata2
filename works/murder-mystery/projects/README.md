# 作品一覧

各作品は`projects/{slug}/`に固定します。進行状態が変わっても移動しません。

新規作成:

```bash
task work:new -- my-work "仮タイトル"
```

日常的に編集するファイル:

```text
projects/{slug}/private/WORK.md
```

GitHub上に見える`README.md`はネタバレなし、`project.yaml`は状態管理用です。
