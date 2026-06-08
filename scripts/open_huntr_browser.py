import asyncio
from playwright.async_api import async_playwright
import os, sys

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        await page.goto("https://huntr.com/bounties/disclose", wait_until="domcontentloaded")
        print("=== HUNTR SUBMIT PAGE OPENED ===")
        print("1. Click 'Open Source Repository'")
        print("2. Log in with GitHub when prompted")
        print("3. Paste report content & submit")
        print("\nReports folder: C:\\Users\\manadger\\Desktop\\moltbook-app\\")
        print("\nFiles to submit:")
        print("  a) agentguard_vulnerability_report.md")
        print("  b) dify_ssrf_vulnerability_report.md")
        print("  c) agentscope_mcp_rce_report.md")
        print("  d) agentscope_mcp_ssrf_report.md")
        print("\nBrowser is open. Close it when done.\n")

        while True:
            await asyncio.sleep(5)
            try:
                if page.is_closed():
                    break
            except:
                break

asyncio.run(main())
