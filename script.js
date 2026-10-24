(() => {
  'use strict';
  const data = window.POTION_DATA;
  const root = document.querySelector('#app');
  const assetRoot = 'public/assets/witch-lab/';
  const assets = new Set();
  const assetNames = ['lab-background', 'witch-neutral', 'witch-happy', 'cauldron-normal', 'cauldron-bubbling', 'ingredient-tile', 'mouse-one', 'mice-five', 'goose-one', 'geese-four', 'sheep-one', 'sheep-six'];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let state;
  let timers = [];
  const arrivingWords = new Map();
  const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const shuffle = items => {
    const result = [...items];
    for (let i = result.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [result[i], result[j]] = [result[j], result[i]]; }
    return result;
  };
  const later = (fn, delay) => { timers.push(setTimeout(fn, reduced.matches ? 40 : delay)); };
  function reset() {
    timers.forEach(clearTimeout); timers = [];
    document.querySelectorAll('.ingredient-flight').forEach(el => el.remove());
    arrivingWords.clear();
    state = { screen: 'start', round: 0, index: 0, selected: new Set(), accepted: [], fixing: false, busy: false, failedBrew: false, failureNotice: false, message: '', mood: '',
      ingredients: shuffle(data.ingredients), forms: shuffle(data.forms).map(q => ({ ...q, options: shuffle(q.options) })),
      phrases: shuffle(data.phrases).map(q => ({ ...q, options: q.options ? shuffle(q.options) : [] })) };
    render();
  }
  function image(name, alt, css = '') { return `<img class="${css}" src="${assetRoot}${name}.png" alt="${esc(alt)}" draggable="false">`; }
  function witch(happy = false) {
    const name = happy ? 'witch-happy' : 'witch-neutral';
    return `<div class="witch-art ${happy ? 'happy' : ''}" role="img" aria-label="A friendly red-haired witch${happy ? ' celebrating' : ''}">${image(name, '')}</div>`;
  }
  function cauldron() {
    const name = state.screen === 'brewing' ? 'cauldron-bubbling' : 'cauldron-normal';
    return `<div class="cauldron ${state.screen === 'brewing' ? 'brewing' : ''} ${state.failedBrew ? 'brew-failed' : ''}" data-drop="cauldron" role="img" aria-label="Magic cauldron. Drop an ingredient here."><div class="steam" aria-hidden="true"><i></i><i></i><i></i></div>${assets.has(name) ? image(name, '') : '<div class="pot-handle left"></div><div class="pot-handle right"></div><div class="pot-body"><span class="pot-star">✧</span></div><div class="pot-rim"></div><div class="potion"><i></i><i></i><i></i></div><div class="pot-feet"></div>'}<div class="hearth"></div><div class="brew-effects" aria-hidden="true"><div class="brew-glow"></div><div class="brew-bubbles"><i></i><i></i><i></i><i></i></div><div class="magic-smoke"><i></i><i></i><i></i></div></div>${failedEffects()}</div>`;
  }
  function failedEffects() {
    if (!state.failedBrew) return '';
    return `<div class="failure-effects" aria-hidden="true"><svg class="failure-surface" viewBox="0 0 1284 1200"><ellipse class="failed-liquid" cx="650" cy="259" rx="416" ry="40"/><ellipse class="failed-flash" cx="650" cy="251" rx="345" ry="52"/></svg><div class="failed-bubbles"><i></i><i></i><i></i><i></i></div><div class="mud-bubbles"><i></i><i></i><i></i></div><div class="failed-smoke"><i></i><i></i><i></i></div><svg class="failed-sparks" viewBox="0 0 300 270"><path style="--spark-x:-14px;--spark-y:-17px" d="m79 30 2 5 5 2-5 2-2 5-2-5-5-2 5-2Z"/><path style="--spark-x:16px;--spark-y:-13px" d="m222 37 2 4 4 2-4 2-2 4-2-4-4-2 4-2Z"/><circle style="--spark-x:-17px;--spark-y:-8px" cx="83" cy="55" r="2"/><circle style="--spark-x:19px;--spark-y:-5px" cx="220" cy="59" r="2.5"/></svg></div>`;
  }
  function animal(kind, index = 0) {
    return `<div class="animal ${kind}" style="--i:${index}" role="img" aria-label="${kind}">${assets.has(`${kind}-one`) ? image(`${kind}-one`, '') : '<span class="animal-body"></span><span class="animal-tail"></span><span class="animal-head"><i class="animal-ear"></i><i class="animal-eye"></i><i class="animal-nose"></i></span><span class="animal-legs"></span>'}</div>`;
  }
  function animals(round, animate = false, group = false) {
    if (group && assets.has(round.group)) return `<div class="animal-group">${image(round.group, `${round.count} ${round.plural}`)}</div>`;
    return `<div class="animal-row ${animate ? 'multiplying' : ''}" aria-label="${round.count} ${round.plural}">${Array.from({ length: round.count }, (_, i) => animal(round.animal, i)).join('')}</div>`;
  }
  function steps() {
    return `<nav class="potion-steps" aria-label="Potion progress">${data.rounds.map((r, i) => {
      const complete = i < state.round || state.screen === 'final' || (state.screen === 'result' && i === state.round);
      const active = i === state.round && !complete;
      const status = complete ? 'completed' : active ? 'active' : 'locked';
      return `<div class="step ${complete ? 'complete' : active ? 'current' : 'locked'}" aria-label="Potion ${i + 1}: ${status}" ${active ? 'aria-current="step"' : ''}><svg class="step-cauldron" viewBox="0 0 64 64" aria-hidden="true"><g class="nav-bubbles" fill="none" stroke="#e4d89b" stroke-width="1.8"><circle cx="24" cy="8" r="2.4"/><circle cx="38" cy="6" r="1.8"/><circle cx="45" cy="11" r="2"/></g><path d="M11 27C1 21 0 40 11 37M53 27C63 21 64 40 53 37" fill="none" stroke="#a2754c" stroke-width="3"/><path d="m17 50-3 9h7l3-7m16 0 3 7h7l-3-9" fill="#49353b" stroke="#b58b5c" stroke-width="1.5"/><path d="M10 19C6 36 8 54 32 54S58 36 54 19Z" fill="#4d3b43" stroke="#be955f" stroke-width="2"/><ellipse cx="32" cy="19" rx="23" ry="7" fill="#382d36" stroke="#d8ae70" stroke-width="2.3"/><ellipse class="nav-potion" cx="32" cy="19" rx="19.5" ry="4.2" fill="#b7a563"/><path d="m31 32 1.6 4.4L37 38l-4.4 1.6L31 44l-1.6-4.4L25 38l4.4-1.6Z" fill="#d9b678"/><g class="nav-check"><circle cx="53" cy="11" r="9" fill="#8ea862" stroke="#dce4b7" stroke-width="1"/><path d="m49 11 3 3 5-6" fill="none" stroke="#fff4cf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g></svg><span class="step-label">Potion ${i + 1}</span></div>`;
    }).join('')}</nav>`;
  }
  function card(word, action = 'answer', selected = false) {
    return `<button class="word-card ${selected ? 'selected' : ''} ${selected && arrivingWords.has(word) ? 'ingredient-arriving' : ''}" data-action="${action}" data-word="${esc(word)}" draggable="${action === 'select'}" ${state.busy ? 'disabled' : ''} ${action === 'select' ? `aria-label="${selected ? 'Remove' : 'Add'} ${esc(word)} ${selected ? 'from' : 'to'} cauldron"` : ''}>${esc(word)}${selected ? '<span aria-hidden="true">×</span>' : ''}</button>`;
  }
  function workshop() {
    return `<section class="workshop" aria-label="Witch’s laboratory"><div class="witch-side">${witch()}</div><div class="pot-side">${cauldron()}<p class="failure-notice" role="status" aria-live="polite">${state.failureNotice ? 'POOF! Wrong ingredients! Try again!' : ''}</p></div></section>`;
  }
  function start() {
    return `<section class="start-scene" aria-label="Witch’s Potion Lab"><div class="start-intro"><span class="start-brand">MR. FOXY</span><h1>Witch’s<br><em>Potion Lab</em></h1><p class="start-subtitle">One Becomes Many!</p><p class="start-copy">Help the witch make three magical multiplying potions!</p><button class="primary brew-start" data-action="start">LET'S BREW!<svg class="brew-button-icon" viewBox="0 0 28 28" aria-hidden="true"><path d="m5 24 12-12"/><path d="m20 3 1.7 5.3L27 10l-5.3 1.7L20 17l-1.7-5.3L13 10l5.3-1.7Z"/></svg><svg class="button-sparks" viewBox="0 0 250 80" preserveAspectRatio="none" aria-hidden="true"><path d="m23 8 2 5 5 2-5 2-2 5-2-5-5-2 5-2Z"/><path d="m218 8 1.5 4 4 1.5-4 1.5-1.5 4-1.5-4-4-1.5 4-1.5Z"/><path d="m238 48 1.5 4 4 1.5-4 1.5-1.5 4-1.5-4-4-1.5 4-1.5Z"/></svg></button></div><div class="start-figures" aria-label="The witch and her cauldron in the laboratory"><div class="start-witch">${witch()}</div><div class="wand-sparks" aria-hidden="true"><i>✦</i><i>✧</i><i>✦</i></div><div class="start-cauldron">${cauldron()}<div class="start-bubbles" aria-hidden="true"><i></i><i></i><i></i></div></div></div></section>`;
  }
  function challenge() {
    const r = data.rounds[state.round];
    const sequential = state.round > 0;
    const count = sequential ? state.index : state.selected.size;
    const done = sequential && count >= r.total;
    const overfilled = !sequential && count > r.total;
    const heading = state.round === 0
      ? `<header class="round-heading"><div class="parchment-heading"><span class="potion-kicker">Potion 1</span><h1>${esc(r.title)}</h1><svg class="heading-spark" viewBox="0 0 28 28" aria-hidden="true"><path d="m14 3 2.7 8.3L25 14l-8.3 2.7L14 25l-2.7-8.3L3 14l8.3-2.7Z"/><circle cx="24" cy="4" r="1.5"/><circle cx="4" cy="24" r="1"/></svg></div><p class="round-instruction">${esc(r.instruction)}</p></header>`
      : state.round === 1
        ? `<header class="round-heading goose-heading"><div class="goose-title-slot"><div class="parchment-heading"><span class="potion-kicker">POTION 2 · THE GOOSE POTION</span><h1>Make It Plural!</h1><svg class="heading-spark" viewBox="0 0 28 28" aria-hidden="true"><path d="m14 3 2.7 8.3L25 14l-8.3 2.7L14 25l-2.7-8.3L3 14l8.3-2.7Z"/></svg><svg class="heading-spark small-spark" viewBox="0 0 28 28" aria-hidden="true"><path d="m14 3 2.7 8.3L25 14l-8.3 2.7L14 25l-2.7-8.3L3 14l8.3-2.7Z"/></svg></div></div>${!done ? `<p class="question-count">Question ${state.index + 1} / ${r.total}</p><p class="round-instruction">Choose the correct plural form.</p>` : ''}</header>`
        : `<header class="round-heading"><h1><span class="potion-title">Potion ${state.round + 1} · </span>${esc(r.title)}</h1>${!done ? `<p class="question-count">Question ${state.index + 1} / ${r.total}</p><p class="round-instruction">${esc(r.instruction)}</p>` : ''}</header>`;
    let content;
    if (state.round === 0) {
      content = `<div class="tray-label ingredient-help"><span>Tap a word or drag it to the cauldron</span></div><div class="word-grid">${state.ingredients.filter(q => !state.selected.has(q.word)).map(q => card(q.word, 'select')).join('')}</div><div class="selected-zone ${overfilled ? 'overfilled' : ''}"><div class="tray-label">IN YOUR CAULDRON <span>${state.selected.size} / ${r.total} ingredients</span></div><div class="selected-words">${[...state.selected].map(w => card(w, 'select', true)).join('') || '<p class="empty-note">Your recipe starts with a word…</p>'}</div><p class="small-note">Tap an added word to put it back.</p></div>`;
    } else if (done) {
      content = '<p class="recipe-ready">All ingredients are in the cauldron.</p>';
    } else {
      const q = state.round === 1 ? state.forms[state.index] : state.phrases[state.index];
      const prompt = state.round === 1
        ? `<div class="transformation"><span class="question-word">${esc(q.word)}</span><span class="transformation-arrow" aria-hidden="true">→</span><span class="question-mark" aria-hidden="true">?</span></div>`
        : `<div class="question-word phrase-word">${esc(q.phrase)}</div>`;
      const answers = state.round === 2 && !state.fixing
        ? '<div class="decision-buttons"><button class="secondary" data-action="keep">KEEP IT! <span>✓</span></button><button class="secondary fix" data-action="fix">FIX IT! <span>✧</span></button></div>'
        : `<div class="answer-cards">${q.options.map(w => card(w)).join('')}</div>`;
      content = `${prompt}${answers}`;
    }
    const brewButton = !sequential || done
      ? `<button class="primary brew" data-action="brew" ${state.busy ? 'disabled' : ''}>${state.screen === 'brewing' ? 'BREWING…' : 'BREW THE POTION!'}<svg class="game-brew-icon" viewBox="0 0 28 28" aria-hidden="true"><path d="m5 24 12-12"/><path d="m20 3 1.7 5.3L27 10l-5.3 1.7L20 17l-1.7-5.3L13 10l5.3-1.7Z"/></svg></button>` : '';
    return `${steps()}<div class="game-layout">${workshop()}<section class="recipe-panel ${sequential ? 'round-sequential' : 'round-selection'}" aria-label="Recipe ingredients">${heading}<div class="recipe-content">${content}</div><p class="feedback ${state.mood}" role="status" aria-live="polite">${esc(state.message)}</p><div class="game-bottom"><div class="recipe-progress ${overfilled ? 'overfilled' : ''}"><div><span>${sequential ? 'Ingredients collected:' : 'Ingredients selected'}</span><strong>${count}<small> / ${r.total}</small></strong></div><div class="progress-track" role="progressbar" aria-label="${sequential ? 'Ingredients collected' : 'Selected ingredients'}" aria-valuemin="0" aria-valuemax="${r.total}" aria-valuenow="${Math.min(count, r.total)}"><span style="width:${Math.min(100, count / r.total * 100)}%"></span></div></div>${brewButton}</div></section></div>`;
  }
  function result() {
    const r = data.rounds[state.round];
    return `${steps()}<section class="result-screen"><span class="eyebrow">POTION 0${state.round + 1} · SUCCESSFULLY BREWED</span><h1>A little multiplying magic!</h1><p class="result-intro">One ${r.animal}. A swirl of magic. Meet the ${r.plural}!</p><div class="result-stage"><div class="result-spark" aria-hidden="true">✧</div>${animals(r, true)}</div><h2 class="result-equation" style="--reveal:${reduced.matches ? 0 : r.count * 0.45 + 0.35}s">1 ${r.animal} <span>→</span> ${r.count} ${r.plural}</h2><p class="feedback" role="status">Beautifully brewed, little spellmaker.</p><button class="primary" data-action="next">${state.round < 2 ? 'NEXT POTION' : 'SEE THE MAGIC'} <span>→</span></button></section>`;
  }
  function final() {
    return `<section class="final-screen"><header class="final-heading"><h1>MAGIC COMPLETE!</h1><p>You did it! All three multiplying potions are ready!</p></header><div class="final-scene"><svg class="final-spell-lines" aria-hidden="true"><g class="final-trails">${data.rounds.map((_, i) => `<path class="spell-trail" pathLength="1" style="--trail-at:${.75 + i * 2}s"/>`).join('')}</g><g class="final-wand-stars"><path d="m-17-19 2 5 5 2-5 2-2 5-2-5-5-2 5-2Z"/><path d="m18 7 1.5 4 4 1.5-4 1.5-1.5 4-1.5-4-4-1.5 4-1.5Z"/><circle cx="-13" cy="17" r="1.5"/></g></svg><div class="final-wand-glow" aria-hidden="true"></div><div class="final-witch">${witch(true)}</div><div class="final-potions">${data.rounds.map((r, i) => `<article class="final-result" style="--one-at:${1.2 + i * 2}s;--group-at:${2 + i * 2}s;--after-at:${2.8 + i * 2}s" aria-label="1 ${r.animal} becomes ${r.count} ${r.plural}"><div class="final-animal-stage"><div class="final-one" aria-hidden="true">${assets.has(`${r.animal}-one`) ? image(`${r.animal}-one`, '') : animal(r.animal)}</div><div class="final-many">${animals(r, false, true)}</div><div class="final-puff" aria-hidden="true"></div><div class="final-bubbles" aria-hidden="true"><i></i><i></i><i></i></div><svg class="final-result-sparks" viewBox="0 0 200 180" aria-hidden="true"><path d="m22 25 2 6 6 2-6 2-2 6-2-6-6-2 6-2Z"/><path d="m175 55 2 5 5 2-5 2-2 5-2-5-5-2 5-2Z"/><circle cx="164" cy="24" r="2"/></svg></div><h2 class="final-caption">1 ${r.animal} <span>→</span> ${r.count} ${r.plural}</h2></article>`).join('')}</div></div><div class="final-controls"><button class="primary final-replay" data-action="restart">PLAY AGAIN<svg class="final-button-star" viewBox="0 0 28 28" aria-hidden="true"><path d="m14 3 2.7 8.3L25 14l-8.3 2.7L14 25l-2.7-8.3L3 14l8.3-2.7Z"/><path d="m24 2 1 3 3 1-3 1-1 3-1-3-3-1 3-1Z"/></svg></button></div></section>`;
  }
  function layoutFinalMagic() {
    if (state.screen !== 'final') return;
    const scene = root.querySelector('.final-scene');
    const sprite = root.querySelector('.final-witch .witch-art > img');
    const svg = root.querySelector('.final-spell-lines');
    if (!scene || !sprite || !svg) return;
    if (!sprite.complete || !sprite.naturalWidth) {
      sprite.addEventListener('load', layoutFinalMagic, { once: true });
      return;
    }
    const room = scene.getBoundingClientRect();
    const box = sprite.getBoundingClientRect();
    const scale = Math.min(box.width / sprite.naturalWidth, box.height / sprite.naturalHeight);
    const width = sprite.naturalWidth * scale;
    const height = sprite.naturalHeight * scale;
    // Wand tip in the original, unmodified witch-happy.png; account for contain fit.
    const x = box.left - room.left + (box.width - width) / 2 + width * .792;
    const entryOffset = new DOMMatrixReadOnly(getComputedStyle(root.querySelector('.final-witch')).transform).m42;
    const y = box.bottom - room.top - entryOffset - height + height * .029;
    svg.setAttribute('viewBox', `0 0 ${room.width} ${room.height}`);
    root.querySelector('.final-wand-stars').setAttribute('transform', `translate(${x} ${y})`);
    const glow = root.querySelector('.final-wand-glow');
    glow.style.left = `${x}px`; glow.style.top = `${y}px`;
    const stages = [...root.querySelectorAll('.final-animal-stage')];
    root.querySelectorAll('.spell-trail').forEach((path, i) => {
      const target = stages[i].getBoundingClientRect();
      const endX = target.left - room.left + target.width / 2;
      const endY = target.top - room.top + target.height * .5;
      path.setAttribute('d', `M ${x} ${y} C ${x + (endX - x) * .32} ${y - 30}, ${endX - 45} ${endY - 65}, ${endX} ${endY}`);
    });
  }
  function render(focusHeading = false) {
    const oldBar = root.querySelector('.progress-track > span');
    const sameRound = root.dataset.round === String(state.round + 1);
    const previousFill = oldBar ? oldBar.getBoundingClientRect().width / oldBar.parentElement.clientWidth * 100 : null;
    root.className = `screen-${state.screen} theme-${data.rounds[state.round].color}`;
    root.dataset.round = String(state.round + 1);
    root.innerHTML = state.screen === 'start' ? start() : state.screen === 'result' ? result() : state.screen === 'final' ? final() : challenge();
    const newBar = root.querySelector('.progress-track > span');
    if (newBar && sameRound && previousFill !== null && !reduced.matches) {
      const targetFill = newBar.style.width;
      newBar.style.width = `${previousFill}%`;
      void newBar.offsetWidth;
      requestAnimationFrame(() => { if (newBar.isConnected) newBar.style.width = targetFill; });
    }
    root.querySelectorAll('button').forEach(b => { if (state.busy) b.disabled = true; });
    if (state.screen === 'final') requestAnimationFrame(layoutFinalMagic);
    if (focusHeading) { const h = root.querySelector('h1'); h.tabIndex = -1; h.focus({ preventScroll: true }); window.scrollTo({ top: 0, behavior: 'instant' }); }
  }
  function feedback(message, mood = 'error', button) {
    state.message = message; state.mood = mood;
    const el = root.querySelector('.feedback'); if (el) { el.textContent = message; el.className = `feedback ${mood}`; }
    if (button) { button.classList.remove('shake'); void button.offsetWidth; button.classList.add('shake'); }
  }
  // Capture document coordinates before a render removes the actual source card.
  function cardOrigin(element) {
    if (!element) return null;
    const rect = element.getBoundingClientRect();
    const width = Math.min(rect.width, 240);
    return { x: rect.left + window.scrollX + (rect.width - width) / 2, y: rect.top + window.scrollY, width, height: rect.height };
  }
  function flyIngredient(word, origin) {
    if (!origin || reduced.matches) return;
    const pot = root.querySelector('.cauldron');
    if (!pot) return;
    const target = pot.getBoundingClientRect();
    const flight = document.createElement('span');
    flight.className = 'word-card ingredient-flight';
    flight.setAttribute('aria-hidden', 'true');
    flight.textContent = word;
    Object.entries({ left: `${origin.x}px`, top: `${origin.y}px`, width: `${origin.width}px`, height: `${Math.min(origin.height, 64)}px`,
      '--flight-x': `${target.left + window.scrollX + target.width / 2 - origin.x - origin.width / 2}px`,
      '--flight-y': `${target.top + window.scrollY + target.height * .21 - origin.y - Math.min(origin.height, 64) / 2}px`
    }).forEach(([key, value]) => flight.style.setProperty(key, value));
    document.body.append(flight);
    flight.addEventListener('animationend', () => {
      flight.remove();
      const currentPot = root.querySelector('.cauldron');
      if (currentPot && state.screen === 'game') {
        currentPot.classList.remove('ingredient-received');
        void currentPot.offsetWidth;
        currentPot.classList.add('ingredient-received');
      }
    }, { once: true });
    // Also clean up if motion preferences change while a flight is running.
    later(() => flight.remove(), 850);
  }
  function accept(word, source) {
    if (state.busy) return;
    const origin = cardOrigin(source);
    state.busy = true; state.accepted.push(word);
    feedback('Lovely! Into the cauldron.', 'success'); render();
    const departing = source?.matches('.word-card')
      ? [...root.querySelectorAll('.word-card')].find(card => card.dataset.word === word)
      : root.querySelector('.question-word');
    if (departing && !reduced.matches) departing.classList.add('ingredient-departed');
    flyIngredient(word, origin);
    later(() => { state.index++; state.busy = false; state.fixing = false; state.message = ''; render(); }, 850);
  }
  function select(word, source) {
    if (state.screen !== 'game' || state.round !== 0 || state.busy || !data.ingredients.some(q => q.word === word)) return;
    const adding = !state.selected.has(word);
    const origin = cardOrigin(source);
    const arrival = {};
    if (adding && origin && !reduced.matches) arrivingWords.set(word, arrival);
    else arrivingWords.delete(word);
    if (state.selected.has(word)) state.selected.delete(word); else state.selected.add(word);
    state.message = ''; state.failureNotice = false; render();
    // All first-round selections look alike: reveal no correctness before BREW.
    if (adding) flyIngredient(word, origin);
    if (arrivingWords.get(word) === arrival) later(() => {
      if (arrivingWords.get(word) !== arrival) return;
      arrivingWords.delete(word);
      [...root.querySelectorAll('.selected-words .word-card')].find(card => card.dataset.word === word)?.classList.remove('ingredient-arriving');
    }, 800);
  }
  function failBrew() {
    state.busy = true; state.failedBrew = true; state.failureNotice = reduced.matches; state.message = '';
    render();
    if (!reduced.matches) later(() => {
      state.failureNotice = true;
      const notice = root.querySelector('.failure-notice');
      if (notice) notice.textContent = 'POOF! Wrong ingredients! Try again!';
    }, 1100);
    // Keep the original recipe intact. Reduced motion uses a brief static purple tint.
    const finish = () => {
      state.busy = false; state.failedBrew = false; state.failureNotice = true;
      render();
    };
    timers.push(setTimeout(finish, reduced.matches ? 180 : 2800));
  }
  function brew() {
    if (state.screen !== 'game' || state.busy) return;
    if (state.round === 0) {
      const correct = data.ingredients.filter(q => q.correct).map(q => q.word);
      if (state.selected.size !== correct.length || !correct.every(w => state.selected.has(w))) return failBrew();
    } else if (state.index !== data.rounds[state.round].total) return;
    state.busy = true; state.screen = 'brewing'; state.message = ''; state.failureNotice = false; render();
    // A phone may have scrolled down to BREW: bring the actual effect into view.
    const scene = root.querySelector('.workshop');
    const bounds = scene.getBoundingClientRect();
    if (bounds.top < 0 || bounds.bottom > window.innerHeight) scene.scrollIntoView({ block: 'center', behavior: reduced.matches ? 'instant' : 'smooth' });
    later(() => { state.screen = 'result'; render(true); later(() => { state.busy = false; root.querySelectorAll('button').forEach(b => { b.disabled = false; }); }, data.rounds[state.round].count * 450 + 500); }, 1800);
  }
  root.addEventListener('click', e => {
    const button = e.target.closest('button[data-action]'); if (!button || button.disabled || state.busy) return;
    const action = button.dataset.action;
    if (action === 'start' && state.screen === 'start') { state.screen = 'game'; render(true); }
    else if (action === 'restart' && state.screen === 'final') { reset(); state.screen = 'game'; render(true); }
    else if (action === 'select') select(button.dataset.word, button);
    else if (action === 'brew') brew();
    else if (action === 'next' && state.screen === 'result') {
      if (state.round === 2) state.screen = 'final';
      else { state.round++; state.screen = 'game'; state.index = 0; state.accepted = []; state.fixing = false; state.message = ''; }
      render(true);
    } else if (state.screen === 'game' && state.round > 0) {
      const q = state.round === 1 ? state.forms[state.index] : state.phrases[state.index]; if (!q) return;
      if (action === 'answer' && (state.round === 1 || state.fixing)) {
        if (button.dataset.word === q.answer) accept(q.answer, button); else feedback('Try again!', 'error', button);
      } else if (action === 'keep' && state.round === 2 && !state.fixing) {
        if (q.keep) accept(q.answer, root.querySelector('.question-word')); else feedback('Try again!', 'error', button);
      } else if (action === 'fix' && state.round === 2 && !state.fixing) {
        if (q.keep) feedback('Try again!', 'error', button);
        else { state.fixing = true; state.message = 'Choose a better phrase.'; state.mood = ''; render(); }
      }
    }
  });
  root.addEventListener('dragstart', e => {
    const b = e.target.closest('[data-action="select"]'); if (!b || state.busy) return e.preventDefault();
    e.dataTransfer.setData('text/plain', b.dataset.word); e.dataTransfer.effectAllowed = 'move';
  });
  root.addEventListener('dragover', e => { const pot = e.target.closest('[data-drop]'); if (pot && state.round === 0 && !state.busy) { e.preventDefault(); pot.classList.add('drag-over'); } });
  root.addEventListener('dragleave', e => { const pot = e.target.closest('[data-drop]'); if (pot) pot.classList.remove('drag-over'); });
  root.addEventListener('drop', e => { if (!e.target.closest('[data-drop]')) return; e.preventDefault(); const word = e.dataTransfer.getData('text/plain'); if (!state.selected.has(word)) select(word); });
  reset();
  window.addEventListener('resize', layoutFinalMagic, { passive: true });
  // Missing PNGs are expected: test availability before rendering an image.
  Promise.all(assetNames.map(name => new Promise(resolve => {
    const img = new Image(); img.onload = () => { assets.add(name); resolve(); }; img.onerror = resolve; img.src = `${assetRoot}${name}.png`;
  }))).then(() => {
    if (assets.has('lab-background')) {
      document.querySelector('.lab-backdrop').style.backgroundImage = `url("${assetRoot}lab-background.png")`;
      document.documentElement.classList.add('has-lab-art');
    }
    if (assets.has('ingredient-tile')) {
      document.documentElement.style.setProperty('--tile-image', `url("${assetRoot}ingredient-tile.png")`);
      document.documentElement.classList.add('has-ingredient-art');
    }
    render();
  });
})();
