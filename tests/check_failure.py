"""Wrong recipes, capped progress and a replayable local cauldron reaction."""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work' / 'failure'
OUT.mkdir(parents=True, exist_ok=True)
MESSAGE = 'POOF! Wrong ingredients! Try again!'


def selected(page):
    return page.locator('.selected-words .word-card').evaluate_all('(els)=>els.map(e=>e.dataset.word).sort()')


def assert_capped(page, count, amber):
    expect(page.locator('.recipe-progress strong')).to_have_text(f'{count} / 6')
    assert page.locator('.recipe-progress').evaluate('(e)=>e.classList.contains("overfilled")') == amber
    assert page.locator('.selected-zone').evaluate('(e)=>e.classList.contains("overfilled")') == amber
    assert page.locator('.progress-track>span').evaluate('(e)=>e.getBoundingClientRect().width<=e.parentElement.clientWidth+1')
    expect(page.locator('[data-action=brew]')).to_be_enabled()


with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    for width, height in [(1366,768),(390,844),(320,740)]:
        page = browser.new_page(viewport={'width':width,'height':height}, has_touch=width<900)
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.emulate_media(reduced_motion='reduce')
        page.goto((ROOT / 'index.html').as_uri())
        page.wait_for_function('document.querySelector(".witch-art img")?.complete')
        data = page.evaluate('POTION_DATA')
        page.locator('[data-action=start]').click()
        brew = page.locator('[data-action=brew]')
        # Empty recipes use the same error path, including reduced-motion feedback.
        brew.click()
        expect(page.locator('.failure-notice')).to_have_text(MESSAGE)
        expect(brew).to_be_enabled()
        assert selected(page) == []
        choices = [q['word'] for q in sorted(data['ingredients'], key=lambda q: q['correct'])]
        for word in choices[:8]:
            page.get_by_role('button',name=f'Add {word} to cauldron',exact=True).click()
        assert_capped(page,8,True)
        amber = page.locator('.progress-track>span').evaluate('(e)=>getComputedStyle(e).backgroundColor')
        before=selected(page)
        # Document coordinates ignore Playwright scrolling the BREW button into view.
        position = '(e)=>{const r=e.getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height};}'
        layout=page.locator('.pot-side').evaluate(position)
        scroll=page.evaluate('({height:document.documentElement.scrollHeight,width:document.documentElement.scrollWidth})')
        page.emulate_media(reduced_motion='no-preference')
        brew.click()
        expect(brew).to_be_disabled()
        expect(page.locator('.cauldron')).to_have_class(re.compile('brew-failed'))
        brew.evaluate('(e)=>{e.click();e.click();}')
        page.locator('.selected-words .word-card').first.evaluate('(e)=>e.click()')
        assert selected(page) == before
        expect(page.locator('.cauldron>img')).to_have_attribute('src', re.compile('cauldron-normal.png'))
        # The real animation clock: green, POOF smoke, then purple liquid.
        page.wait_for_function('Number(getComputedStyle(document.querySelector(".failed-liquid")).opacity)>.6')
        assert page.locator('.failed-liquid').evaluate('(e)=>getComputedStyle(e).fill') == 'rgb(167, 198, 110)'
        page.screenshot(path=str(OUT/f'{width}-green.png'),full_page=True)
        page.wait_for_function('Number(getComputedStyle(document.querySelector(".failed-smoke")).opacity)>.75')
        page.screenshot(path=str(OUT/f'{width}-poof.png'),full_page=True)
        expect(page.locator('.failure-notice')).to_have_text(MESSAGE)
        page.wait_for_function('getComputedStyle(document.querySelector(".failed-liquid")).fill === "rgb(130, 100, 135)"')
        assert page.locator('.failed-liquid').evaluate('(e)=>getComputedStyle(e).fill') == 'rgb(130, 100, 135)'
        page.screenshot(path=str(OUT/f'{width}-purple.png'),full_page=True)
        assert page.locator('.pot-side').evaluate(position) == layout
        assert page.evaluate('({height:document.documentElement.scrollHeight,width:document.documentElement.scrollWidth})') == scroll
        if width>=900:
            assert scroll['height']<=height and scroll['width']<=width
        # Effects stay inside the cauldron's horizontal extent, clear of the cards.
        assert page.locator('.failed-smoke').evaluate('e=>{const r=e.getBoundingClientRect(),p=e.closest(".cauldron").getBoundingClientRect();return r.left>=p.left&&r.right<=p.right;}')
        expect(brew).to_be_enabled()
        assert selected(page) == before
        expect(page.locator('.failure-effects')).to_have_count(0)
        # Repeat the same failure; it must run from the beginning again.
        brew.click()
        expect(brew).to_be_disabled()
        expect(page.locator('.failure-effects')).to_have_count(1)
        expect(page.locator('.failure-notice')).to_be_empty()
        expect(brew).to_be_enabled()
        assert selected(page) == before
        page.emulate_media(reduced_motion='reduce')
        for word in choices[6:8]:
            page.get_by_role('button',name=f'Remove {word} from cauldron',exact=True).click()
        assert_capped(page,6,False)
        assert page.locator('.progress-track>span').evaluate('(e)=>getComputedStyle(e).backgroundColor') != amber
        # Six words with the wrong composition must still fail.
        assert any(not q['correct'] for q in data['ingredients'] if q['word'] in selected(page))
        brew.click()
        expect(page.locator('.failure-notice')).to_have_text(MESSAGE)
        assert page.locator('.failed-liquid').evaluate('(e)=>getComputedStyle(e).fill') == 'rgb(130, 100, 135)'
        assert page.locator('.failed-smoke').evaluate('(e)=>getComputedStyle(e).display') == 'none'
        expect(brew).to_be_enabled()
        for word in selected(page):
            page.get_by_role('button',name=f'Remove {word} from cauldron',exact=True).click()
        for q in data['ingredients']:
            if q['correct']:
                page.get_by_role('button',name=f'Add {q["word"]} to cauldron',exact=True).click()
        page.emulate_media(reduced_motion='no-preference')
        brew.click()
        expect(page.locator('.cauldron')).to_have_class(re.compile('brewing'))
        expect(page.locator('.failure-effects')).to_have_count(0)
        expect(page.locator('.failure-notice')).to_be_empty()
        expect(page.locator('#app')).to_have_class(re.compile('screen-result'))
        assert not errors,errors
        page.close()
        print(f'PASS {width}x{height}: error phases, retained recipe, duplicate lock, repeat, 8/6 cap, six wrong, successful correction.',flush=True)
    browser.close()
