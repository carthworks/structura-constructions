#!/usr/bin/env python3
"""Screenshot the site for visual QA."""
import sys, asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:8080/index.html"
OUT = "assets/raw/shots"
SECTIONS = [
    ("hero", "#top"),
    ("about", "#about"),
    ("services", "#services"),
    ("projects", "#projects"),
    ("engine", "#expertise"),
    ("case", "#case-study"),
    ("system", "#marketing-system"),
    ("why", "#why"),
    ("testimonials", "#testimonials"),
    ("insights", "#insights"),
    ("locations", "#locations"),
    ("faq", "#faq"),
    ("contact", "#contact"),
    ("footer", "footer"),
]

async def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 1440
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 900
    tag = sys.argv[3] if len(sys.argv) > 3 else "desk"
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        page = await browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        errors = []
        page.on("console", lambda m: errors.append(f"[{m.type}] {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(f"[pageerror] {e}"))
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(1400)
        # force all reveals visible for full-page shot
        await page.evaluate("""() => {
            document.querySelectorAll('[data-reveal]').forEach(el => el.classList.add('is-visible'));
        }""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/00-{tag}-full.png", full_page=True)
        for name, sel in SECTIONS:
            try:
                el = await page.query_selector(sel)
                if not el: continue
                await el.scroll_into_view_if_needed()
                await page.wait_for_timeout(650)
                await page.screenshot(path=f"{OUT}/{name}-{tag}.png")
            except Exception as e:
                print("skip", name, e)
        print("ERRORS:", errors[:12] if errors else "none")
        await browser.close()

asyncio.run(main())
