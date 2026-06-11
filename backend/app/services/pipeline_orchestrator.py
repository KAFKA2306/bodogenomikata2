import logging
from typing import Any

from app.services.asset_service import asset_service
from app.services.game_master_service import GameMasterService
from app.services.notebooklm_service import notebooklm_service

logger = logging.getLogger("services.orchestrator")


class PipelineOrchestrator:
    """
    The Master Conductor.
    Links Knowledge, Visuals, and Human-Readable Exports.
    """

    def __init__(self):
        self.game_master = GameMasterService()

    async def execute_full_pipeline(self, game_name: str) -> dict[str, Any]:
        # 1. Knowledge Phase: Reconstruct the High-Res Guide
        logger.info(f"--- Pipeline Step 1: Knowledge Acquisition for {game_name} ---")
        game_data = await self.game_master.generate_and_save_game_guide(game_name)

        # 2. Preparation Phase: Export to Markdown
        logger.info("--- Pipeline Step 2: Preparing source for NotebookLM ---")
        markdown_source = self.game_master.export_as_markdown(game_data)

        # 3. Visual Phase: Generate Unified Assets via NotebookLM
        logger.info("--- Pipeline Step 3: Generating Visual Assets via NotebookLM ---")
        assets = await notebooklm_service.generate_unified_assets(game_data, markdown_source)

        # 4. Human Phase: Export to local files
        logger.info("--- Pipeline Step 4: Exporting human-readable files ---")
        # Refresh game_data with latest assets before saving
        game_data["infographics"] = assets
        asset_dir = asset_service.save_game_assets(game_data)
        logger.info(f"✓ Assets exported to: {asset_dir}")

        # 5. Success Completion
        logger.info(f"--- Pipeline Complete for {game_name}! ---")

        # Fetch the very latest state from DB to return
        from app.core import sqlite_client

        return sqlite_client.get_game_by_slug(game_data["slug"])


orchestrator = PipelineOrchestrator()
