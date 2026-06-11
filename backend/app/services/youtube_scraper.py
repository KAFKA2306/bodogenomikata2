import logging
import urllib.parse

from playwright.async_api import async_playwright

logger = logging.getLogger("services.youtube_scraper")


async def scrape_youtube_videos(query: str, limit: int = 5) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        search_query = f"{query} ボードゲーム ルール"
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"
        logger.info(f"Navigating to YouTube: {url}")
        await page.goto(url)

        await page.wait_for_selector("ytd-video-renderer", timeout=10000)

        video_elements = await page.query_selector_all("ytd-video-renderer")
        videos = []
        for elem in video_elements[:limit]:
            title_elem = await elem.query_selector("a#video-title")
            if not title_elem:
                continue
            title = (await title_elem.text_content() or "").strip()
            href = await title_elem.get_attribute("href") or ""
            if "v=" not in href:
                continue
            video_id = href.split("v=")[-1].split("&")[0]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

            duration = None
            dur_elem = await elem.query_selector("span.ytd-thumbnail-overlay-time-status-renderer")
            if dur_elem:
                duration = (await dur_elem.text_content() or "").strip()

            views_count = 0
            meta_elems = await elem.query_selector_all("span.inline-metadata-item")
            for me in meta_elems:
                text = await me.text_content() or ""
                if "回" in text or "views" in text:
                    digits = "".join(filter(str.isdigit, text))
                    if digits:
                        views_count = int(digits)
                        break

            videos.append(
                {
                    "video_id": video_id,
                    "title": title,
                    "url": video_url,
                    "thumbnail_url": thumbnail_url,
                    "duration": duration,
                    "views_count": views_count,
                }
            )

        await browser.close()
        return videos
