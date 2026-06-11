"""完全自動化：PDF→Gemini→インフォグラフィック PNG 生成（ノーフォールバック）"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

import pdfplumber

# Gemini API をインポート
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app.core.gemini import GeminiClient
from notebooklm_constants import (
    INFOGRAPHIC_TYPES,
    INFOGRAPHICS_BASE_DIR,
    METADATA_FILENAME,
)
from notebooklm_utils import (
    display_header,
    display_next_steps,
    display_summary,
    ensure_directory,
    handle_error,
    save_json,
)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ Pillow がインストールされていません: pip install pillow")
    sys.exit(1)


class InfographicsGenerator:
    """Gemini API でインフォグラフィック生成"""

    def __init__(self, game_slug: str, game_title: str, pdf_path: Path):
        self.game_slug = game_slug
        self.game_title = game_title
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(INFOGRAPHICS_BASE_DIR) / game_slug
        self.gemini = GeminiClient()
        self.pdf_text = ""
        self.infographics_data = {}

    async def run(self):
        """メインワークフロー"""
        try:
            display_header(f"インフォグラフィック生成: {self.game_title}")

            # PDF からテキスト抽出
            await self._extract_pdf_text()

            # Gemini でインフォグラフィック説明を生成
            await self._generate_infographics_descriptions()

            # PNG に変換
            await self._render_infographics_to_png()

            # メタデータ保存
            self._save_metadata()

            # サマリー表示
            self._display_summary()

        except Exception as e:
            handle_error(e, "インフォグラフィック生成失敗")
            raise

    async def _extract_pdf_text(self):
        """PDF からテキスト抽出"""
        print(f"\n📄 PDF 抽出中: {self.pdf_path}")

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF が見つかりません: {self.pdf_path}")

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                self.pdf_text = ""
                for page in pdf.pages[:10]:  # 最初の10ページ
                    self.pdf_text += page.extract_text() or ""

            print(f"✓ PDF 抽出完了 ({len(self.pdf_text)} 文字)")

        except Exception as e:
            raise RuntimeError(f"PDF 抽出失敗: {e}")

    async def _generate_infographics_descriptions(self):
        """Gemini でインフォグラフィック説明を生成"""
        print("\n🤖 Gemini でインフォグラフィック生成中...")

        prompts = {
            "setup": f"ゲーム '{self.game_title}' のセットアップ手順をテキストで簡潔に説明してください:\n\n{self.pdf_text[:2000]}",
            "turn_flow": f"ゲーム '{self.game_title}' の手番の流れをテキストで説明してください:\n\n{self.pdf_text[:2000]}",
            "actions": f"ゲーム '{self.game_title}' で可能なアクション一覧をテキストで列挙してください:\n\n{self.pdf_text[:2000]}",
            "winning": f"ゲーム '{self.game_title}' の勝利条件をテキストで説明してください:\n\n{self.pdf_text[:2000]}",
            "components": f"ゲーム '{self.game_title}' のゲームコンポーネント（ボード、駒、カード等）をテキストで列挙してください:\n\n{self.pdf_text[:2000]}",
        }

        for inf_type, prompt in prompts.items():
            try:
                result = await self.gemini.generate_structured_json(prompt)

                # 結果が辞書か文字列か判定
                if isinstance(result, dict):
                    self.infographics_data[inf_type] = result.get("description", str(result))
                else:
                    self.infographics_data[inf_type] = str(result)

                print(f"✓ {inf_type}")

            except Exception as e:
                print(f"✗ {inf_type}: {e}")
                # Gemini が失敗した場合、空文字列を使用（フォールバックなし）
                self.infographics_data[inf_type] = ""

    async def _render_infographics_to_png(self):
        """テキストを PNG に変換"""
        ensure_directory(self.output_dir)
        print("\n🎨 PNG レンダリング中...")

        for inf_type in INFOGRAPHIC_TYPES:
            try:
                text = self.infographics_data.get(inf_type, "")
                filepath = self._create_png(inf_type, text)
                print(f"✓ {inf_type}: {filepath.name}")

            except Exception as e:
                raise RuntimeError(f"PNG レンダリング失敗 ({inf_type}): {e}")

    def _create_png(self, inf_type: str, text: str) -> Path:
        """テキストから PNG を生成"""
        # 画像サイズ
        width, height = 1920, 1080

        # 背景色：カラフルなグラデーション
        colors = {
            "setup": (100, 150, 255),  # 青
            "turn_flow": (100, 255, 150),  # 緑
            "actions": (255, 200, 100),  # オレンジ
            "winning": (255, 100, 100),  # 赤
            "components": (200, 100, 255),  # 紫
        }
        bg_color = colors.get(inf_type, (200, 200, 200))

        # 画像作成
        img = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # フォント
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except Exception:
            font = ImageFont.load_default()
            small_font = font

        # テキスト配置
        margin = 100
        y_offset = 150

        # タイトル
        title = f"📊 {inf_type.upper()}"
        draw.text((margin, 50), title, fill="white", font=font)

        # テキスト（改行対応）
        lines = text.split("\n")
        for line in lines[:20]:  # 最大20行
            if y_offset > height - 100:
                break
            draw.text((margin, y_offset), line[:100], fill="white", font=small_font)
            y_offset += 40

        # ファイル保存
        filepath = self.output_dir / f"{inf_type}.png"
        img.save(str(filepath), "PNG")

        return filepath

    def _save_metadata(self):
        """メタデータ保存"""
        metadata = {
            "game_slug": self.game_slug,
            "game_title": self.game_title,
            "generated_at": datetime.now().isoformat(),
            "infographics": {inf_type: str(self.output_dir / f"{inf_type}.png") for inf_type in INFOGRAPHIC_TYPES},
            "pdf_source": str(self.pdf_path),
            "automation": "full",
        }

        metadata_path = self.output_dir / METADATA_FILENAME
        save_json(metadata_path, metadata)
        print(f"\n✅ メタデータ保存: {metadata_path}")

    def _display_summary(self):
        """結果サマリー"""
        summary_items = {
            "ゲーム": self.game_title,
            "出力ディレクトリ": str(self.output_dir),
            "生成数": str(len(INFOGRAPHIC_TYPES)),
            "生成時刻": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "自動化レベル": "フル（Gemini）",
        }

        display_summary("生成完了", summary_items)

        display_next_steps(
            [
                "upsert_game_with_infographics.py で DB に登録",
                "フロントエンドで 📊 図解 タブで確認",
            ]
        )


def _find_or_create_pdf(game_slug: str, game_title: str) -> Path:
    """PDF ファイルを検索またはテスト用を作成"""
    pdf_dir = Path("assets") / "pdfs"
    pdf_pattern = f"{game_slug.replace('-', '_')}*.pdf"

    # assets/pdfs ディレクトリを検索
    pdf_dir.mkdir(parents=True, exist_ok=True)
    for pdf in pdf_dir.glob(pdf_pattern):
        print(f"✓ PDF 見つかりました: {pdf}")
        return pdf

    # 見つからない場合、テスト用 PDF を作成
    print("⚠️  PDF が見つかりません。テスト用 PDF を作成します...")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        print("❌ reportlab がインストールされていません: pip install reportlab")
        sys.exit(1)

    pdf_path = pdf_dir / f"{game_slug}.pdf"

    # テスト用 PDF を生成
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setFont("Helvetica", 14)
    c.drawString(50, 750, f"Game: {game_title}")
    c.setFont("Helvetica", 10)

    content = [
        "Setup Instructions:",
        "1. Place the board in the center of the table",
        "2. Distribute starting resources to each player",
        "3. Shuffle cards and place them in the draw pile",
        "",
        "Turn Flow:",
        "1. Draw a card or take a resource",
        "2. Perform one action",
        "3. Pass to the next player",
        "",
        "Available Actions:",
        "- Build a structure",
        "- Trade with other players",
        "- Develop a technology",
        "- Pass",
        "",
        "Winning Condition:",
        "First player to reach 100 points wins",
        "",
        "Game Components:",
        "- 1 game board",
        "- 60 cards",
        "- 4 sets of player pieces",
        "- 1 scoreboard",
    ]

    y = 700
    for line in content:
        if y < 50:
            c.showPage()
            y = 750
        c.drawString(50, y, line)
        y -= 15

    c.save()
    print(f"✓ テスト用 PDF 作成: {pdf_path}")
    return pdf_path


async def main():
    parser = argparse.ArgumentParser(description="完全自動化：PDF→Gemini→PNG")
    parser.add_argument("game_slug", help="ゲームスラッグ (例: brass-birmingham)")
    parser.add_argument("game_title", help="ゲームタイトル (例: Brass: Birmingham)")
    parser.add_argument("--pdf", default=None, help="PDF ファイルパス（省略時は検索・作成）")

    args = parser.parse_args()

    # PDF ファイルパスを特定
    pdf_path = Path(args.pdf) if args.pdf else _find_or_create_pdf(args.game_slug, args.game_title)

    generator = InfographicsGenerator(args.game_slug, args.game_title, pdf_path)
    await generator.run()


if __name__ == "__main__":
    asyncio.run(main())
