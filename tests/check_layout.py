"""Viewport and clipping checks against real gameplay; no skipped rounds."""
from pathlib import Path
import json
import re
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work' / 'layout'
OUT.mkdir(parents=True, exist_ok=True)
checks = []


def verify(page, label, desktop=True):
    issues = page.evaluate('''() => {
      const issues=[];
      if(document.documentElement.scrollWidth>innerWidth) issues.push('horizontal page overflow');
      if(document.documentElement.scrollHeight>innerHeight+1 && innerWidth>=900) issues.push('vertical page overflow: '+document.documentElement.scrollHeight);
      for(const e of document.querySelectorAll('.potion-steps,.round-heading,.recipe-panel,.game-bottom,.word-card:not(.ingredient-flight),.decision-buttons button,.brew,.witch-art img,.cauldron>img')){
        const s=getComputedStyle(e),r=e.getBoundingClientRect();
        if(s.display==='none'||s.visibility==='hidden'||!r.width) continue;
        if(innerWidth>=900 && (r.top<-.5||r.bottom>innerHeight+.5||r.left<-.5||r.right>innerWidth+.5)) issues.push(e.className+' outside viewport '+JSON.stringify(r.toJSON()));
        if(e.scrollHeight>e.clientHeight+2 && ['auto','scroll','hidden'].includes(s.overflowY)) issues.push(e.className+' clipped/scrolling');
        if(e.matches('.word-card') && parseFloat(s.fontSize)<20) issues.push('small word text');
        for(let parent=e.parentElement;parent && parent!==document.body;parent=parent.parentElement){
          const ps=getComputedStyle(parent),p=parent.getBoundingClientRect();
          const portraitCrop=e.matches('.witch-art img') && parent.matches('.witch-side');
          if(portraitCrop){
            // Only the lower body may be deliberately cropped. Hat, face, wand
            // and hand occupy the top 55% of the original full-height PNG.
            if(r.top<p.top-1||r.top+r.height*.55>p.bottom+1) issues.push('portrait cuts a required character feature');
          }else if(['hidden','clip','auto','scroll'].includes(ps.overflowY) && (r.top<p.top-1||r.bottom>p.bottom+1)) issues.push(e.className+' clipped by '+parent.className);
        }
      }
      if(document.querySelector('.potion-steps').getBoundingClientRect().height>70)issues.push('tall progress navigation');
      if(document.querySelectorAll('.step-cauldron').length!==3)issues.push('missing SVG potion indicators');
      if(!document.querySelector('.recipe-panel .round-heading'))issues.push('task heading separated from recipe');
      for(const e of document.querySelectorAll('.workshop,.recipe-panel')){
        const s=getComputedStyle(e);
        if(s.backgroundColor!=='rgba(0, 0, 0, 0)' || s.backgroundImage!=='none' || s.boxShadow!=='none')issues.push('visible scene panel');
      }
      if(document.querySelector('.workshop .window,.workshop .shelf,.pot-caption'))issues.push('artificial lab decoration remains');
      return issues;
    }''')
    assert not issues, f'{label}: {issues}'
    checks.append(label)


def screenshot(page, size, name):
    if size == (1366, 768):
        page.screenshot(path=str(OUT / f'1366x768-{name}.png'))


with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    for size in [(1280,720),(1366,768),(1440,900),(1920,1080),(390,844),(320,740)]:
        page = browser.new_page(viewport={'width':size[0],'height':size[1]}, has_touch=size[0]<900)
        page.emulate_media(reduced_motion='reduce')
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto((ROOT / 'index.html').as_uri())
        page.wait_for_function('document.querySelector(".witch-art img")?.complete')
        data=page.evaluate('window.POTION_DATA')
        page.locator('[data-action=start]').click()
        verify(page,f'{size} round 1 initial')
        screenshot(page,size,'round-1')
        # Every selection density, including all twelve selected, must fit.
        for item in data['ingredients']:
            page.get_by_role('button',name=f"Add {item['word']} to cauldron",exact=True).click()
            verify(page,f'{size} selected {item["word"]}')
        page.locator('[data-action=brew]').click()
        expect(page.locator('.failure-notice')).to_contain_text('Wrong ingredients!')
        expect(page.locator('[data-action=brew]')).to_be_enabled()
        verify(page,f'{size} recipe error visible')
        for item in data['ingredients']:
            if not item['correct']:
                page.get_by_role('button',name=f"Remove {item['word']} from cauldron",exact=True).click()
        verify(page,f'{size} round 1 ready')
        screenshot(page,size,'round-1-ready')
        for round_index in range(3):
            if round_index:
                screenshot(page,size,f'round-{round_index+1}-question')
                questions=data['forms'] if round_index==1 else data['phrases']
                for i in range(len(questions)):
                    current=page.locator('.question-word').inner_text()
                    q=next(q for q in questions if q.get('word',q.get('phrase'))==current)
                    verify(page,f'{size} round {round_index+1}: {current}')
                    if round_index==2:
                        page.locator('[data-action=keep]' if q.get('keep') else '[data-action=fix]').click()
                        if not q.get('keep'):
                            verify(page,f'{size} corrections: {current}')
                    if round_index==1 or not q.get('keep'):
                        page.locator('[data-action=answer]').filter(has_text=re.compile('^'+re.escape(q['answer'])+'$')).click()
                    expect(page.locator('[role=progressbar]')).to_have_attribute('aria-valuenow',str(i+1))
                verify(page,f'{size} round {round_index+1} BREW visible')
                screenshot(page,size,f'round-{round_index+1}')
            page.locator('[data-action=brew]').click()
            expect(page.locator('#app')).to_have_class(re.compile('screen-result'))
            expect(page.locator('[data-action=next]')).to_be_enabled()
            page.locator('[data-action=next]').click()
        expect(page.locator('h1')).to_have_text('MAGIC COMPLETE!')
        assert not errors,errors
        page.close()
        print(f'PASS {size}: all rounds, selections, corrections and BREW buttons',flush=True)
    browser.close()
(OUT / 'results.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2),encoding='utf-8')
print(f'PASS {len(checks)} layout checks')
