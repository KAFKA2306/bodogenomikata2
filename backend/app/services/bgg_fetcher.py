import asyncio
import json
import re
from typing import Any

from playwright.async_api import async_playwright

BGG_BASE_URL = "https://boardgamegeek.com/boardgame"


class BGGFetcher:
    async def fetch_game_by_id(self, game_id: int) -> dict[str, Any]:
        async with async_playwright() as p:
            # Add a user agent to look more human
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Navigate without waiting for full idle
            await page.goto(f"{BGG_BASE_URL}/{game_id}", wait_until="domcontentloaded")

            # Deterministic wait for the preload data
            await page.wait_for_selector("script:has-text('GEEK.geekitemPreload')", timeout=10000)

            content = await page.content()
            await browser.close()
            return self._parse_html_response(content, game_id)

    async def search_game(self, title: str) -> int | None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Perform search
            search_url = f"https://boardgamegeek.com/geeksearch.php?action=search&q={title.replace(' ', '+')}"
            await page.goto(search_url, wait_until="domcontentloaded")

            # Find the first result link
            # The search results page typically has links like /boardgame/12345/...
            try:
                # Look for the first link that starts with /boardgame/
                selector = "a[href^='/boardgame/']"
                await page.wait_for_selector(selector, timeout=5000)
                link = await page.get_attribute(selector, "href")

                # Extract the ID
                match = re.search(r"/boardgame/(\d+)", link)
                if match:
                    await browser.close()
                    return int(match.group(1))
            except Exception:
                pass

            await browser.close()
            return None

    def _parse_html_response(self, html: str, game_id: int) -> dict[str, Any]:
        # Robust regex to find the preload data
        match = re.search(r"GEEK\.geekitemPreload\s*=\s*(\{.*?\});", html, re.DOTALL)
        if not match:
            # Try a second pattern just in case
            match = re.search(r"geekitemPreload\s*:\s*(\{.*?\})", html, re.DOTALL)

        data = json.loads(match.group(1))
        item = data["item"]
        
        from app.utils import slugify
        links = item.get("links", {})
        
        def parse_link_list(lst):
            res = []
            for x in (lst or []):
                try:
                    res.append({
                        "name": x["name"],
                        "bgg_id": int(x["objectid"]),
                        "slug": slugify(x["name"])
                    })
                except (KeyError, ValueError, TypeError):
                    continue
            return res

        return {
            "id": str(game_id),
            "name": item["name"],
            "description": item["description"],
            "image": item["imageurl"],
            "yearpublished": item["yearpublished"],
            "minplayers": item["minplayers"],
            "maxplayers": item["maxplayers"],
            "playingtime": item["maxplaytime"],
            "minage": item["minage"],
            "designers": parse_link_list(links.get("boardgamedesigner")),
            "publishers": parse_link_list(links.get("boardgamepublisher")),
            "expansions": parse_link_list(links.get("boardgameexpansion")),
            "expands": parse_link_list(links.get("expandsboardgame")),
        }
