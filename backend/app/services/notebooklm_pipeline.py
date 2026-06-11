import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class NotebookLMPipeline:
    def __init__(self):
        self.bin = shutil.which("notebooklm")

    async def _gen(self, mode: str, game: dict[str, Any], ext: str, extra: list[str]) -> str | None:
        if not self.bin:
            return None
        slug = game["slug"]
        content = f"# {game['title']}\n\n{game.get('description', '')}\n\n{game.get('rules_summary', '')}"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            tmp = f.name
        out = f"/tmp/{slug}_{mode}.{ext}"
        try:
            subprocess.run(
                [self.bin, "generate", mode, "--input", tmp, "--output", out, "--language", "ja", *extra], check=True
            )
            return out
        finally:
            Path(tmp).unlink(missing_ok=True)

    async def generate_slides(self, g: dict[str, Any]) -> str | None:
        return await self._gen("slides", g, "pdf", [])

    async def generate_video(self, g: dict[str, Any]) -> str | None:
        return await self._gen("video", g, "mp4", ["--duration", "5m"])

    async def generate_summary(self, g: dict[str, Any]) -> str | None:
        out = await self._gen("summary", g, "md", ["--length", "medium"])
        if not out:
            return None
        return Path(out).read_text(encoding="utf-8")

    async def generate_all(self, g: dict[str, Any]) -> dict[str, str]:
        if not self.bin:
            return {}
        res = {
            "slides": await self.generate_slides(g),
            "video": await self.generate_video(g),
            "summary": await self.generate_summary(g),
        }
        res = {k: v for k, v in res.items() if v is not None}
        return res


pipeline = NotebookLMPipeline()
