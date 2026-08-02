# 秘密本文のローカル構造

このテンプレートを各作品の`private/`へコピーします。作品側の`private/`はGit追跡しません。

推奨構造:

```text
private/
├── truth.yaml
├── evidence-map.yaml
├── characters/
├── handouts/
├── endings/
└── production-secrets/
```

ここへ置くもの:

- 犯人、死因、真相、時系列の完全版
- 各人物の秘密と個別目標
- ハンドアウト本文
- 証拠と真相の対応表
- エンディング条件と結末本文

`project.yaml`には秘密本文そのものではなく、アクセス制御された保存先の参照IDだけを記録します。
