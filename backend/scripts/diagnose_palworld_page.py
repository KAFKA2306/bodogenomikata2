import asyncio

from playwright.async_api import async_playwright

URLS = [
    "https://en.palworld-official-cardgame.com/cardlist/searchresults?expansion=EBP01",
    "https://palworld-official-cardgame.com/cardlist/searchresults?expansion=EBP01",
]


async def inspect(url: str) -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        responses: list[tuple[int, str, str]] = []
        console_messages: list[str] = []
        page.on(
            "response",
            lambda response: responses.append(
                (response.status, response.request.resource_type, response.url)
            )
            if response.request.resource_type in {"xhr", "fetch"}
            else None,
        )
        page.on("console", lambda message: console_messages.append(f"{message.type}: {message.text}"))
        navigation = await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000)
        body = await page.locator("body").inner_text()
        print(f"PAGE {url}")
        print(f"NAV_STATUS {navigation.status if navigation else 'none'}")
        print(f"FINAL_URL {page.url}")
        print(f"TITLE {await page.title()}")
        print(f"BODY_HEAD {body[:2000]!r}")
        print("FETCH_XHR")
        for status, resource_type, response_url in responses:
            print(status, resource_type, response_url)
        print("CONSOLE")
        for message in console_messages[-30:]:
            print(message)
        await browser.close()


async def main() -> None:
    for url in URLS:
        await inspect(url)


if __name__ == "__main__":
    asyncio.run(main())
