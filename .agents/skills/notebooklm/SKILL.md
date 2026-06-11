---
name: notebooklm
description: Mastering Google NotebookLM via notebooklm-py. Generates unified summary sheets, turn guides, and scoring checklists directly through internal APIs.
---

# NotebookLM Intelligence Skill (Latest March 2026)

NotebookLM を「魔法の清書エンジン」として使いこなすための知能だもんっ✨

## 🚀 The 'notebooklm-py' Revolution

RuleScribe Games v2 は、ブラウザ操作（Playwright Browser）を卒業し、非公式 Python API **`notebooklm-py`** による直接通信へと進化しました💕

### Key Capabilities:
1.  **Direct RPC Communication**: ブラウザを介さず、Google の内部 API と直接お話しするよっ✨
2.  **Official Artifacts**: チャットで質問するより、`generate_report(report_format='briefing_doc')` を使うほうが、NotebookLM の清書能力を 100% 発揮できるんだもんっ！
3.  **Unified Assets**: 「サマリーシート（Briefing Doc）」「スタディガイド（Scoring/Turn Flow）」「手番早見表」を統一された最高品質で出力するよっ💕

## 🛠️ Usage Patterns

### Initialization (The Right Way):
```python
from notebooklm import NotebookLMClient
async with await NotebookLMClient.from_storage() as client:
    # Auth is handled automatically from ~/.notebooklm/storage_state.json
```

### Knowledge Injection:
```python
# Sources must have 'title' and 'content'
await client.sources.add_text(notebook_id=nb_id, title="Official Rules", content=markdown_text)
```

### Unified Generation:
- **サマリーシート**: `client.artifacts.generate_report(nb_id, report_format="briefing_doc")`
- **詳細ガイド**: `client.artifacts.generate_studio_artifact(nb_id, artifact_type="study_guide")`
- **手番早見表**: `client.chat.ask(nb_id, question="手番早見表を作って")`

## 💎 Zero-Fat Rules for NotebookLM
- **No Manual Selectors**: `page.click('button')` などの不安定なセレクターはもう使わない。すべて API メソッドで完結させるっ💕
- **Markdown-First**: 入力ソースは必ず `GameMasterService` が生成した綺麗な Markdown を使うこと✨
- **Success Path Only**: `wait_for_completion` などの同期処理を適切に行い、失敗したら CDD の精神で潔くクラッシュするもんっ！
