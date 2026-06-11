"""共有定数と設定"""

# NotebookLMインフォグラフィック生成設定
INFOGRAPHIC_TYPES = [
    "setup",
    "turn_flow",
    "actions",
    "winning",
    "components",
]

# ファイルシステム設定
INFOGRAPHICS_BASE_DIR = "assets/infographics"
METADATA_FILENAME = "metadata.json"

# UIガイダンス メッセージ
NOTEBOOKLM_URL = "https://notebooklm.google.com"

USER_GUIDE_STEPS = [
    "NotebookLMのブラウザが自動で開きます",
    "Googleアカウントでログインしてください",
    "PDF ファイルをアップロード欄にドラッグ＆ドロップするか、クリックして選択してください",
    "アップロード後、以下の5つの図解生成をリクエストしてください:",
    "  • セットアップ手順（Setup）",
    "  • 手番の流れ（Turn Flow）",
    "  • アクション一覧（Actions）",
    "  • 勝利条件（Winning Conditions）",
    "  • ゲームコンポーネント（Components）",
    "",
    "すべての図解が生成されたら、このスクリプトに戻ってEnterキーを押してください",
]

GUIDE_PAUSE_MESSAGE = "\n✋ 図解の生成が完了したら、Enterキーを押してください...\n"

MANUAL_UPLOAD_MESSAGE = f"""
⚠️  NotebookLMは自動ログインをブロックするため、手動でアップロードしてください:

1. ブラウザで次のURLを開いてください: {NOTEBOOKLM_URL}
2. ログイン後、PDFをアップロード
3. 生成をリクエスト
4. このスクリプトに戻ってEnterを押してください

"""
