import asyncio
import logging
from pathlib import Path
from typing import Any

import notebooklm

from app.core import sqlite_client

logger = logging.getLogger("services.notebooklm")


class NotebookLMService:
    """
    Advanced 'Zero-Fat' Service with Slide Generation & Download.
    """

    def __init__(self):
        pass

    async def generate_unified_assets(self, game_data: dict[str, Any], markdown_source: str) -> dict[str, str]:
        logger.info(f"🚀 [REAL API] Opening NotebookLM for visual generation: {game_data['title']}")

        async with await notebooklm.NotebookLMClient.from_storage() as client:
            # 1. Create Notebook
            nb = await client.notebooks.create(title=f"RuleScribe: {game_data['title']}")
            nb_id = nb.id

            # 2. Add Source
            await client.sources.add_text(notebook_id=nb_id, title="Official Rules", content=markdown_source)

            assets = {}

            # A. Generate Reports (Briefing Doc)
            logger.info("Generating Summary Report...")
            await client.artifacts.generate_report(notebook_id=nb_id, report_format="briefing_doc")

            # B. Generate Slides (THE VISUALS)
            logger.info("Generating Visual Slide Deck...")
            # According to our signature check, generate_slides is the way!
            await client.artifacts.generate_slides(notebook_id=nb_id)

            # Wait for both to finish (NotebookLM takes time for slides)
            logger.info("Waiting for generations to complete (30s)...")
            await asyncio.sleep(30)

            # 3. Fetch & Download Artifacts
            artifacts = await client.artifacts.list(notebook_id=nb_id)

            # Create a temp directory for downloads
            temp_dir = Path("assets/temp_downloads")
            temp_dir.mkdir(parents=True, exist_ok=True)

            for art in artifacts:
                if "Briefing Doc" in art.title:
                    assets["summary_sheet"] = art.content
                elif art.kind == notebooklm.ArtifactType.SLIDE_DECK:
                    # Download the real PDF slide
                    logger.info(f"Downloading Slides PDF: {art.title}")
                    pdf_path = temp_dir / f"{game_data['slug']}_slides.pdf"
                    await client.artifacts.download_slides(notebook_id=nb_id, output_path=str(pdf_path), format="pdf")
                    assets["slides_pdf_path"] = str(pdf_path)

            # C. Essential Guides via Chat
            logger.info("Generating Detailed Guides via Chat...")
            resp_score = await client.chat.ask(
                notebook_id=nb_id, question="最終得点計算のチェックリストを作成してください。"
            )
            assets["scoring_guide"] = resp_score.answer

            resp_turn = await client.chat.ask(notebook_id=nb_id, question="手番早見表を作成してください。")
            assets["turn_guide"] = resp_turn.answer

            # 4. Persistence
            game_data["infographics"] = assets
            sqlite_client.upsert_game(game_data)

            return assets


notebooklm_service = NotebookLMService()
