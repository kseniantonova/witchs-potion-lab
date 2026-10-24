"""End-to-end checks of the real static page using installed Microsoft Edge."""
from pathlib import Path
import json
import os
import re
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work'
OUT.mkdir(exist_ok=True)
report = []
GAME_URL = os.environ.get('GAME_URL', 'http://127.0.0.1:8000/')


def check(condition, label):
    assert condition, label
    report.append(label)


def button(page, action):
    return page.locator(f'button[data-action="{action}"]')


def exact_word(page, value):
    return page.locator('button.word-card').filter(has_text=re.compile('^' + re.escape(value) + '$'))


def assert_fit(page, label):
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), label)


def run(page, mobile=False, offline=False):
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.emulate_media(reduced_motion='no-preference')
    page.goto((ROOT / 'index.html').as_uri() if offline else GAME_URL)
    page.wait_for_function('document.querySelector(".witch-art img")?.complete')
    check(page.locator('.witch-art img').count() == 1, 'Supplied witch PNG loaded')
    expect(page.locator('h1')).to_contain_text('Potion Lab')
    assert_fit(page, 'Start fits viewport')
    page.screenshot(path=str(OUT / ('mobile-start.png' if mobile else 'desktop-start.png')), full_page=True)
    content = page.evaluate('window.POTION_DATA')
    check(len(content['forms']) == 10 and len(content['phrases']) == 12, 'All 22 sequential tasks present')
    for q in content['forms'] + [q for q in content['phrases'] if not q.get('keep')]:
        check(q['options'].count(q['answer']) == 1 and len(set(q['options'])) == 3, 'Unique correct option: ' + q.get('word', q.get('phrase', '')))
    button(page, 'start').click()
    expect(page.locator('.word-grid .word-card')).to_have_count(12)
    check(button(page, 'next').count() == 0, 'Cannot skip first potion')
    button(page, 'brew').click()
    expect(page.locator('.failure-notice')).to_have_text('POOF! Wrong ingredients! Try again!')
    expect(button(page, 'brew')).to_be_enabled()
    check(page.locator('.screen-result').count() == 0, 'Empty recipe rejected')
    # Exact set required, not merely six cards.
    page.get_by_role('button', name='Add pumpkins to cauldron', exact=True).click()
    flight_target = page.locator('.ingredient-flight').evaluate('''e => {
      const pot=document.querySelector('.cauldron').getBoundingClientRect();
      const x=parseFloat(e.style.left)+parseFloat(e.style.width)/2+parseFloat(e.style.getPropertyValue('--flight-x'));
      const y=parseFloat(e.style.top)+parseFloat(e.style.height)/2+parseFloat(e.style.getPropertyValue('--flight-y'));
      return Math.abs(x-(pot.left+scrollX+pot.width*.5))<1 && Math.abs(y-(pot.top+scrollY+pot.height*.21))<1;
    }''')
    check(flight_target, 'Card flight ends in the cauldron opening')
    added = page.get_by_role('button', name='Remove pumpkins from cauldron', exact=True)
    check(added.evaluate('e=>Number(getComputedStyle(e).opacity)') == 0, 'Selected label waits for the flight')
    expect(added).to_have_css('opacity', '1')
    for q in content['ingredients']:
        if q['correct']:
            page.get_by_role('button', name=f"Add {q['word']} to cauldron", exact=True).click()
    button(page, 'brew').click()
    expect(page.locator('.failure-notice')).to_have_text('POOF! Wrong ingredients! Try again!')
    expect(button(page, 'brew')).to_be_enabled()
    check(page.locator('.selected-words .word-card').count() == 7, 'Wrong recipe preserves selection for correction')
    page.get_by_role('button', name='Remove pumpkins from cauldron', exact=True).click()
    # Round trip a selected word, then use desktop drag-and-drop to return it.
    page.get_by_role('button', name='Remove mice from cauldron', exact=True).click()
    if mobile:
        page.get_by_role('button', name='Add mice to cauldron', exact=True).tap()
    else:
        page.get_by_role('button', name='Add mice to cauldron', exact=True).drag_to(page.locator('[data-drop="cauldron"]'))
    check(page.locator('.selected-words .word-card').count() == 6, 'Tap/remove and drag/tap add work')
    assert_fit(page, 'Round 1 fits viewport')
    page.screenshot(path=str(OUT / ('mobile-round1.png' if mobile else 'desktop-round1.png')), full_page=True)
    brew_result(page, 5, 'mice')
    button(page, 'next').click()
    seen = []
    for _ in range(10):
        current = page.locator('.question-word').inner_text()
        seen.append(current)
        expect(page.locator('.question-count')).to_have_text(f'Question {len(seen)} / 10')
        expect(page.locator('[role="progressbar"]')).to_have_attribute('aria-valuenow', str(len(seen) - 1))
        check(page.locator('.step.complete').count() == 1 and page.locator('.step.locked').count() == 1, 'Potion 2 indicator states are correct')
        if len(seen) in (1, 10):
            page.screenshot(path=str(OUT / f'{page.viewport_size["width"]}-round2-question-{len(seen)}.png'), full_page=True)
        q = next(q for q in content['forms'] if q['word'] == current)
        wrong = next(w for w in q['options'] if w != q['answer'])
        before = page.locator('[role="progressbar"]').get_attribute('aria-valuenow')
        exact_word(page, wrong).click()
        expect(page.locator('.feedback')).to_have_text('Try again!')
        if len(seen) == 1:
            page.screenshot(path=str(OUT / f'{page.viewport_size["width"]}-round2-error.png'), full_page=True)
        check(page.locator('[role="progressbar"]').get_attribute('aria-valuenow') == before, 'Wrong form does not advance: ' + current)
        check(button(page, 'brew').count() == 0, 'Brew unavailable before completing forms')
        page.locator('.word-card').evaluate_all('(els) => { const b=els.find(e=>e.textContent === ' + json.dumps(q['answer']) + '); b.click(); b.click(); b.click(); }')
        check(page.locator('.ingredient-flight').count() == 1, 'Correct card flies once: ' + current)
        if len(seen) == 1:
            expect(page.locator('.question-count')).to_have_text('Question 1 / 10')
            expect(page.locator('[role="progressbar"]')).to_have_attribute('aria-valuenow', '0')
            page.screenshot(path=str(OUT / f'{page.viewport_size["width"]}-round2-correct-flight.png'), full_page=True)
        # Controls lock immediately, one increment per answer.
        expect(page.locator('[role="progressbar"]')).to_have_attribute('aria-valuenow', str(len(seen)))
    check(len(set(seen)) == 10, 'All ten form questions answered exactly once')
    expect(page.locator('[data-action="answer"]')).to_have_count(0)
    expect(button(page, 'brew')).to_be_visible()
    page.screenshot(path=str(OUT / f'{page.viewport_size["width"]}-round2-ready.png'), full_page=True)
    brew_result(page, 4, 'geese')
    button(page, 'next').click()
    for i in range(12):
        current = page.locator('.question-word').inner_text()
        q = next(q for q in content['phrases'] if q['phrase'] == current)
        before = page.locator('[role="progressbar"]').get_attribute('aria-valuenow')
        button(page, 'fix' if q.get('keep') else 'keep').click()
        expect(page.locator('.feedback')).to_have_text('Try again!')
        check(page.locator('[role="progressbar"]').get_attribute('aria-valuenow') == before, 'Wrong judgment rejected: ' + current)
        if q.get('keep'):
            button(page, 'keep').click()
        else:
            button(page, 'fix').click()
            wrong = next(w for w in q['options'] if w != q['answer'])
            exact_word(page, wrong).click()
            expect(page.locator('.feedback')).to_have_text('Try again!')
            check(page.locator('[role="progressbar"]').get_attribute('aria-valuenow') == before, 'Wrong correction does not advance: ' + current)
            exact_word(page, q['answer']).click()
        expect(page.locator('[role="progressbar"]')).to_have_attribute('aria-valuenow', str(i + 1))
        assert_fit(page, 'Round 3 fits viewport: ' + current)
    brew_result(page, 6, 'sheep')
    button(page, 'next').click()
    expect(page.locator('h1')).to_have_text('MAGIC COMPLETE!')
    expect(page.locator('.final-potions article')).to_have_count(3)
    for i, r in enumerate(content['rounds']):
        expect(page.locator('.final-potions article').nth(i).locator('.animal-group img')).to_have_attribute('alt', f"{r['count']} {r['plural']}")
    check(True, 'Final summary uses the three supplied group PNGs')
    expect(button(page, 'restart')).to_be_visible(timeout=10000)
    assert_fit(page, 'Final screen fits viewport')
    page.screenshot(path=str(OUT / ('mobile-final.png' if mobile else 'desktop-final.png')), full_page=True)
    button(page, 'restart').click()
    expect(page.locator('.selected-words .word-card')).to_have_count(0)
    expect(page.locator('[role="progressbar"]')).to_have_attribute('aria-valuenow', '0')
    check(page.locator('.step.current').get_attribute('aria-label') == 'Potion 1: active', 'Replay resets to potion 1')
    check(not errors, 'No JavaScript errors: ' + str(errors))


def brew_result(page, count, plural):
    button(page, 'brew').evaluate('(b) => { b.click(); b.click(); b.click(); }')
    expect(button(page, 'brew')).to_be_disabled()
    expect(page.locator('.cauldron > img')).to_have_attribute('src', re.compile('cauldron-bubbling.png'))
    page.wait_for_function('Number(getComputedStyle(document.querySelector(".magic-smoke")).opacity) > .3')
    check(True, f'Purple smoke after green bubbling: {plural}')
    check(page.locator('.cauldron').evaluate('(el) => { const r=el.getBoundingClientRect(); return r.top>=0 && r.bottom<=innerHeight; }'), f'Cauldron effect visible in viewport: {plural}')
    page.screenshot(path=str(OUT / f'{page.viewport_size["width"]}-{plural}-smoke.png'), full_page=True)
    expect(page.locator('#app')).to_have_class(re.compile('screen-result'))
    expect(page.locator('.result-stage .animal')).to_have_count(count)
    check(page.locator('.result-stage .animal img').count() == count, f'Exactly {count} individual PNGs for {plural}')
    # Freeze only the CSS animation clock, so each reveal can be checked exactly.
    frames = page.evaluate('''() => {
      const animals = [...document.querySelectorAll('.multiplying .animal')];
      const animations = animals.map(el => el.getAnimations()[0]);
      animations.forEach(a => { if(a) a.pause(); });
      const counts = [0, ...animals.slice(1).map((_,i) => (i+1)*450 + 250 + 550)].map(time => {
        animations.forEach(a => { if(a) a.currentTime = time; });
        return animals.filter(el => Number(getComputedStyle(el).opacity) > .95).length;
      });
      animations.forEach(a => { if(a) a.play(); });
      return counts;
    }''')
    check(frames == list(range(1, count + 1)), f'Sequential reveal is exactly 1 through {count}: {frames}')
    expect(page.locator('.result-equation')).to_contain_text(f'{count} {plural}')
    expect(button(page, 'next')).to_be_enabled()
    page.screenshot(path=str(OUT / f'{page.viewport_size["width"]}-{plural}-result.png'), full_page=True)
    check(True, f'Brew locks duplicate clicks and produces exactly {count} {plural}')


with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    desktop = browser.new_context(viewport={'width': 1366, 'height': 768})
    run(desktop.new_page())
    mobile = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    published_run = bool(os.environ.get('GAME_URL'))
    mobile.set_offline(not published_run)
    run(mobile.new_page(), mobile=True, offline=not published_run)
    # Check the smallest target and real (non-reduced) animation lock/reveal.
    animation = browser.new_page(viewport={'width': 320, 'height': 740})
    animation.goto((ROOT / 'index.html').as_uri())
    animation.wait_for_function('document.querySelector(".witch-art img")?.complete')
    button(animation, 'start').click()
    assert_fit(animation, '320px viewport fits')
    for w in ['mice', 'teeth', 'children', 'geese', 'men', 'women']:
        animation.get_by_role('button', name=f'Add {w} to cauldron', exact=True).click()
    button(animation, 'brew').click()
    expect(button(animation, 'brew')).to_be_disabled()
    expect(animation.locator('#app')).to_have_class(re.compile('screen-result'))
    expect(button(animation, 'next')).to_be_disabled()
    expect(button(animation, 'next')).to_be_enabled(timeout=7000)
    check(animation.locator('.multiplying .animal').count() == 5, 'Normal-motion animation and delayed next button verified')
    animation.emulate_media(reduced_motion='reduce')
    check(animation.locator('.multiplying .animal').evaluate_all('(els) => els.every(e=>getComputedStyle(e).animationName === "none")'), 'Reduced motion disables animal animations')
    browser.close()

(OUT / 'test-results.json').write_text(json.dumps({'passed': len(report), 'checks': report}, indent=2), encoding='utf-8')
print(f'PASS: {len(report)} checks; complete desktop and mobile runs, plus normal-motion animation. URL: {GAME_URL}')
