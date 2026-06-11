import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        failed_requests = []
        page.on("requestfailed", lambda req: failed_requests.append(req.url))
        
        # 1. Access the page
        await page.goto("https://bodogenomikata2.pages.dev/")
        
        # Wait for network to be idle
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        # 2. Check for content
        text = await page.inner_text("body")
        
        # 3. Check for specific errors
        if "Server Connection Error" in text:
            print("Found 'Server Connection Error'.")
        elif failed_requests:
            print(f"Network requests failed: {failed_requests}")
        else:
            print("No obvious network errors, and no error text found.")
            print(f"Text snippet: {text[:100]}")
            
        await browser.close()

asyncio.run(run())
