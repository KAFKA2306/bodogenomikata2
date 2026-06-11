import json
import logging
import os
from pathlib import Path
from typing import Any

from pdf2image import convert_from_path

logger = logging.getLogger("services.assets")

ASSETS_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "generated"


class AssetService:
    """
    Service to save AI content and convert PDF slides to human-readable PNG images.
    """

    def save_game_assets(self, game_data: dict[str, Any]) -> Path:
        slug = game_data["slug"]
        game_dir = ASSETS_BASE_DIR / slug
        game_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save Markdown Guides
        rules = (
            json.loads(game_data["rules_content"])
            if isinstance(game_data["rules_content"], str)
            else game_data["rules_content"]
        )
        (game_dir / "guide.md").write_text(
            f"# {game_data['title']} Guide\n\n{json.dumps(rules, indent=2, ensure_ascii=False)}", encoding="utf-8"
        )

        infographics = game_data.get("infographics", {})
        if isinstance(infographics, str):
            infographics = json.loads(infographics)

        for key, content in infographics.items():
            if key == "slides_pdf_path":
                # 2. Convert Slides to PNGs
                self._convert_slides_to_pngs(content, game_dir / "slides")
            else:
                (game_dir / f"{key}.md").write_text(f"# {key.upper()}\n\n{content}", encoding="utf-8")

        return game_dir

    def _convert_slides_to_pngs(self, pdf_path: str, output_dir: Path):
        """
        Convert each page of the PDF slides into a high-quality PNG image.
        """
        if not os.path.exists(pdf_path):
            logger.warning(f"Slides PDF not found at {pdf_path}")
            return

        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Converting slides to PNGs in: {output_dir}")

        try:
            # Convert PDF to list of PIL images
            pages = convert_from_path(pdf_path, dpi=200)

            for i, page in enumerate(pages, 1):
                filename = f"slide_page_{i}.png"
                page.save(output_dir / filename, "PNG")
                logger.info(f"✓ Generated {filename}")

        except Exception as e:
            logger.error(f"Failed to convert slides to PNG: {e}")


asset_service = AssetService()
