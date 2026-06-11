"""共有ユーティリティ: ファイルI/O、JSONシリアライズ、CLI操作"""

import json
import sys
import traceback
from pathlib import Path
from typing import Any


def load_json(filepath: Path) -> dict[str, Any]:
    """JSONファイルを読み込む"""
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {filepath}: {e}")


def save_json(filepath: Path, data: dict[str, Any]) -> None:
    """JSONをファイルに保存"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def ensure_directory(dirpath: Path) -> Path:
    """ディレクトリを作成（既存でもOK）"""
    dirpath.mkdir(parents=True, exist_ok=True)
    return dirpath


def display_header(title: str, width: int = 75) -> None:
    """見出しを表示"""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def display_summary(title: str, items: dict[str, str], width: int = 75) -> None:
    """サマリーを表示"""
    display_header(title, width)
    for key, value in items.items():
        print(f"  {key}: {value}")
    print()


def display_next_steps(steps: list[str]) -> None:
    """次のステップを表示"""
    print("📋 次のステップ:")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    print()


def handle_error(error: Exception, context: str = "") -> None:
    """エラーをハンドリングして表示"""
    print(f"\n❌ エラー: {context}")
    print(f"   {type(error).__name__}: {error}")
    if "--verbose" in sys.argv:
        traceback.print_exc()


def confirm_action(prompt: str) -> bool:
    """ユーザーに確認を取る"""
    response = input(f"\n{prompt} (y/n): ").strip().lower()
    return response == "y"


def wait_for_input(message: str = "") -> None:
    """ユーザー入力待ち"""
    if message:
        print(f"\n{message}")
    input("Enterキーを押して続行...")
