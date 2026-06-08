import asyncio
from playwright.async_api import async_playwright
import json, os

REPORTS_DIR = r"C:\Users\manadger\Desktop\moltbook-app"

REPORTS = [
    {
        "title": "AgentGuard — Unauthenticated Approval Bypass (CVSS 9.1)",
        "repo": "https://github.com/WhitzardAgent/AgentGuard",
        "file": "agentguard_vulnerability_report.md",
        "type": "open_source",
    },
    {
        "title": "Dify — SSRF via httpx.get() Without URL Validation (CVSS 8.6)",
        "repo": "https://github.com/langgenius/dify",
        "file": "dify_ssrf_vulnerability_report.md",
        "type": "open_source",
    },
    {
        "title": "AgentScope — RCE via StdioMCPConfig (CVSS 9.0)",
        "repo": "https://github.com/modelscope/agentscope",
        "file": "agentscope_mcp_rce_report.md",
        "type": "open_source",
    },
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            storage_state="huntr_session.json" if os.path.exists("huntr_session.json") else None,
        )
        page = await context.new_page()

        for i, r in enumerate(REPORTS):
            print(f"\n=== {i+1}/{len(REPORTS)}: {r['title']} ===")
            await page.goto("https://huntr.com/bounties/disclose", wait_until="domcontentloaded")
            await asyncio.sleep(2)

            # Check if logged in
            login_btn = page.locator("text=Log in").or_(page.locator("text=LOG IN")).or_(page.locator('button:has-text("GitHub")'))
            if await login_btn.is_visible():
                print("LOGIN REQUIRED — Please log in with GitHub in the browser window, then press Enter here...")
                input("Press Enter after login...")
                await asyncio.sleep(2)
                await context.storage_state(path="huntr_session.json")
                print("Session saved!")

            # Select report type — Open Source Repository
            os_btn = page.locator("text=Open Source Repository")
            if await os_btn.is_visible():
                await os_btn.click()
                await asyncio.sleep(1.5)

            # Fill repo URL
            repo_input = page.locator('input[placeholder*="github"], input[name*="repo"], input[type="url"]')
            if await repo_input.is_visible():
                await repo_input.fill(r["repo"])
                await asyncio.sleep(0.5)

            # Read report content
            report_path = os.path.join(REPORTS_DIR, r["file"])
            content = open(report_path, "r", encoding="utf-8").read()

            # Fill description
            desc_area = page.locator("textarea")
            if await desc_area.is_visible():
                await desc_area.fill(content[:5000])
                await asyncio.sleep(0.5)

            # Click submit
            submit_btn = page.locator('button[type="submit"], button:has-text("Submit"), button:has-text("Report")')
            if await submit_btn.is_visible():
                await submit_btn.click()
                print("Submitted!")
            else:
                print("Submit button not found — fill manually.")

            await asyncio.sleep(3)

        await browser.close()

asyncio.run(main())
