import asyncio
import json
from collections import Counter

from playwright.async_api import async_playwright

EN_API = "https://en.palworld-official-cardgame.com/manage/card-list-user/list"
JA_API = "https://palworld-official-cardgame.com/manage/card-list-user/list"


def base_id(card_number: str) -> str:
    return card_number[:9]


async def fetch_page(request, api: str, page: int) -> dict:
    response = await request.get(
        api,
        params={
            "expansion": "EBP01",
            "title": "EBP01",
            "page": str(page),
            "per_page": "100",
            "sort": "new",
        },
    )
    payload = await response.json()
    print("API", api, "PAGE", page, "STATUS", response.status, "TOTAL", payload.get("total"), "ITEMS", len(payload.get("items", [])))
    return payload


async def main() -> None:
    async with async_playwright() as playwright:
        request = await playwright.request.new_context()
        en1 = await fetch_page(request, EN_API, 1)
        en2 = await fetch_page(request, EN_API, 2)
        items = en1["items"] + en2["items"]
        ids = [item["card_number"] for item in items]
        bases = [base_id(card_number) for card_number in ids]
        print("EN_IDS", json.dumps(ids, ensure_ascii=False))
        print("EN_TOTAL_ITEMS", len(items))
        print("EN_UNIQUE_IDS", len(set(ids)))
        print("EN_LOGICAL_BASES", len(set(bases)))
        print("EN_RARITIES", json.dumps(Counter(item["rare"] for item in items), ensure_ascii=False, sort_keys=True))
        duplicate_ids = sorted(card_number for card_number, count in Counter(ids).items() if count > 1)
        print("EN_DUPLICATE_IDS", json.dumps(duplicate_ids))
        print("EN_PAGE2", json.dumps(en2["items"], ensure_ascii=False))

        ja1 = await fetch_page(request, JA_API, 1)
        print("JA_TOTAL", ja1.get("total"))
        print("JA_ITEMS", json.dumps(ja1.get("items", []), ensure_ascii=False))
        await request.dispose()


if __name__ == "__main__":
    asyncio.run(main())
