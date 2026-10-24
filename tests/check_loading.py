"""Slow background and later-round PNGs must not expose partial scenes."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge', headless=True)
        for width, height in [(1366, 768), (390, 844)]:
            page = await browser.new_page(viewport={'width': width, 'height': height})
            background = asyncio.Event()
            later_rounds = asyncio.Event()
            initial = ['lab-background', 'witch-neutral', 'cauldron-normal', 'ingredient-tile']

            async def delay_image(route):
                name = route.request.url.rsplit('/', 1)[-1].removesuffix('.png')
                if name == 'lab-background':
                    await background.wait()
                elif name not in initial:
                    await later_rounds.wait()
                else:
                    await asyncio.sleep(.1)
                await route.continue_()

            await page.route('**/*.png', delay_image)
            await page.goto((ROOT / 'index.html').as_uri(), wait_until='domcontentloaded')
            await page.wait_for_timeout(250)
            for selector in ['.start-figures', '.lab-backdrop']:
                assert await page.locator(selector).evaluate('(e)=>getComputedStyle(e).visibility') == 'hidden'
            await expect(page.locator('[data-action=start]')).to_be_disabled()
            background.set()
            await expect(page.locator('[data-action=start]')).to_be_enabled()
            assert not later_rounds.is_set()
            assert await page.locator('.start-figures').evaluate('(e)=>getComputedStyle(e).visibility') == 'visible'
            assert await page.locator('.lab-backdrop').evaluate('(e)=>getComputedStyle(e).backgroundImage.includes("lab-background.png") && getComputedStyle(e).visibility === "visible"')
            assert await page.locator('.start-figures img').evaluate_all('(els)=>els.every(e=>e.complete && e.naturalWidth>0)')
            later_rounds.set()
            await page.reload()
            await expect(page.locator('[data-action=start]')).to_be_enabled()
            await page.locator('[data-action=start]').click()
            assert await page.locator('.word-grid .word-card').count() == 12
            await page.close()

        page = await browser.new_page()
        await page.route('**/lab-background.png', lambda route: route.abort())
        await page.goto((ROOT / 'index.html').as_uri())
        await expect(page.locator('.art-load-error')).to_be_visible()
        await expect(page.locator('[data-action=start]')).to_be_disabled()
        assert await page.locator('.start-figures').evaluate('(e)=>getComputedStyle(e).visibility') == 'hidden'
        await browser.close()
    print('PASS: coherent scene on desktop/mobile, deferred later-round PNGs, reload and failed-asset handling.')


asyncio.run(main())
