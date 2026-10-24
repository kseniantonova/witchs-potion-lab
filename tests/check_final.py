"""Verify the final celebration after completing actual grammar rounds."""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work' / 'final'
OUT.mkdir(parents=True, exist_ok=True)


def finish(page, normal_final=True):
    page.emulate_media(reduced_motion='reduce')
    if page.locator('[data-action=start]').count():
        page.locator('[data-action=start]').click()
    data = page.evaluate('POTION_DATA')
    for item in data['ingredients']:
        if item['correct']:
            page.get_by_role('button', name=f"Add {item['word']} to cauldron", exact=True).click()
    for ri in range(3):
        if ri:
            questions = data['forms'] if ri == 1 else data['phrases']
            for i in range(len(questions)):
                current = page.locator('.question-word').inner_text()
                q = next(q for q in questions if q.get('word', q.get('phrase')) == current)
                if ri == 2:
                    page.locator('[data-action=keep]' if q.get('keep') else '[data-action=fix]').click()
                if ri == 1 or not q.get('keep'):
                    page.locator('[data-action=answer]').filter(has_text=re.compile('^' + re.escape(q['answer']) + '$')).click()
                expect(page.locator('[role=progressbar]')).to_have_attribute('aria-valuenow', str(i + 1))
        page.locator('[data-action=brew]').click()
        expect(page.locator('[data-action=next]')).to_be_enabled()
        if ri == 2 and normal_final:
            page.emulate_media(reduced_motion='no-preference')
        page.locator('[data-action=next]').click()
    page.wait_for_function('document.querySelector(".spell-trail")?.hasAttribute("d")')


def frame(page, ms):
    return page.evaluate('''ms => {
      document.querySelector('.final-screen').getAnimations({subtree:true}).forEach(a => {a.pause();a.currentTime=ms;});
      return [...document.querySelectorAll('.final-result')].map(el=>['.final-one','.final-many'].map(sel=>{
        const s=getComputedStyle(el.querySelector(sel));return s.visibility!=='hidden' && Number(s.opacity)>.01;
      }));
    }''', ms)


def fit(page):
    issues = page.evaluate('''() => {
      const issues=[];
      if(document.documentElement.scrollWidth>innerWidth || document.documentElement.scrollHeight>innerHeight+1) issues.push('page overflow');
      for(const e of document.querySelectorAll('.final-heading,.final-witch img,.final-many img,.final-caption,.final-replay')){
        const r=e.getBoundingClientRect();
        if(r.left<-.5 || r.right>innerWidth+.5 || r.top<-.5 || r.bottom>innerHeight+.5)issues.push(e.className+' outside viewport');
      }
      for(const e of document.querySelectorAll('.final-result')){
        if(e.querySelector('.final-many img').getBoundingClientRect().bottom>e.querySelector('.final-caption').getBoundingClientRect().top)issues.push('animal overlaps caption');
      }
      return issues;
    }''')
    assert not issues, (page.viewport_size, issues)


with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 768})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto((ROOT / 'index.html').as_uri())
    page.wait_for_function('document.querySelector(".witch-art img")?.complete')
    finish(page)
    for ms, expected in [
        (0, [[False,False],[False,False],[False,False]]),
        (1600, [[True,False],[False,False],[False,False]]),
        (2300, [[False,True],[False,False],[False,False]]),
        (3600, [[False,True],[True,False],[False,False]]),
        (4300, [[False,True],[False,True],[False,False]]),
        (5600, [[False,True],[False,True],[True,False]]),
        (7600, [[False,True],[False,True],[False,True]])
    ]:
        assert frame(page, ms) == expected, ms
        if ms in (1600,3600,5600,7600):
            page.screenshot(path=str(OUT / f'1366x768-{ms}ms.png'))
    assert page.locator('.final-many img').evaluate_all('(els)=>els.map(e=>e.alt)') == ['5 mice','4 geese','6 sheep']
    assert page.locator('.spell-trail').evaluate_all('(els)=>els.every(e=>e.getAttribute("d").startsWith("M "))')
    for width, height in [(1280,720),(1366,768),(1440,900),(1920,1080),(390,844),(320,740)]:
        page.set_viewport_size({'width':width,'height':height})
        frame(page, 7600)
        fit(page)
        page.screenshot(path=str(OUT / f'{width}x{height}-complete.png'))
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('.final-one').evaluate_all('(els)=>els.every(e=>getComputedStyle(e).display==="none")')
    assert page.locator('.final-many').evaluate_all('(els)=>els.every(e=>getComputedStyle(e).opacity==="1")')
    page.locator('[data-action=restart]').click()
    expect(page.locator('.selected-words .word-card')).to_have_count(0)
    expect(page.locator('[role=progressbar]')).to_have_attribute('aria-valuenow','0')
    page.set_viewport_size({'width':1366,'height':768})
    finish(page)
    # A second completion creates fresh animations, with no old visible groups.
    assert page.locator('.final-many').evaluate_all('(els)=>els.every(e=>getComputedStyle(e).opacity==="0")')
    page.wait_for_function('getComputedStyle(document.querySelector(".final-replay")).opacity === "1"', timeout=10000)
    assert page.locator('.final-many').evaluate_all('(els)=>els.every(e=>getComputedStyle(e).opacity==="1")')
    fit(page)
    page.screenshot(path=str(OUT / '1366x768-replayed-complete.png'))
    assert not errors, errors
    browser.close()
print('PASS: sequential single/group counts, exact supplied PNGs, six viewports, reduced motion, full replay and real animation completion.')
