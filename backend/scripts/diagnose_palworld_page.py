import asyncio
import json
import re

from playwright.async_api import async_playwright

EN_SEARCH = "https://en.palworld-official-cardgame.com/cardlist/searchresults?expansion=EBP01"
EN_API = "https://en.palworld-official-cardgame.com/manage/card-list-user/list?expansion=EBP01&title=EBP01&page=1&per_page=500&sort=new"
JA_HOME = "https://palworld-official-cardgame.com/"
JA_API = "https://palworld-official-cardgame.com/manage/card-list-user/list?expansion=EBP01&title=EBP01&page=1&per_page=500&sort=new"
CARD_RE = re.compile(r"EBP01-\d{3}(?:SSP|OSR|SP|SR)?")


async def dump_api(request, label: str, url: str) -> None:
    response = await request.get(url)
    text = await response.text()
    ids = sorted(set(CARD_RE.findall(text)))
    print(label, "STATUS", response.status)
    print(label, "CONTENT_TYPE", response.headers.get("content-type"))
    print(label, "BODY_HEAD", text[:12000])
    print(label, "UNIQUE_IDS", len(ids))
    print(label, "IDS", json.dumps(ids, ensure_ascii=False))


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        navigation = await page.goto(EN_SEARCH, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)
        body = await page.locator("body").inner_text()
        print("EN_PAGE_STATUS", navigation.status if navigation else None)
        print("EN_PAGE_BODY_HEAD", body[:1200])

        request = await playwright.request.new_context()
        await dump_api(request, "EN_API", EN_API)
        await dump_api(request, "JA_API", JA_API)

        ja_page = await browser.new_page()
        ja_navigation = await ja_page.goto(JA_HOME, wait_until="domcontentloaded")
        await ja_page.wait_for_timeout(3000)
        anchors = await ja_page.locator('a[href*="cardlist"]').evaluate_all(
            "els => els.map(el => ({text: (el.textContent || '').trim(), href: el.href}))"
        )
        print("JA_HOME_STATUS", ja_navigation.status if ja_navigation else None)
        print("JA_CARDLIST_ANCHORS", json.dumps(anchors, ensure_ascii=False))

        await request.dispose()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
