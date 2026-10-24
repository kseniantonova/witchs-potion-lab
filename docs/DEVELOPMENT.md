# Witch’s Potion Lab — One Becomes Many!

An English grammar game for Mr. Foxy, ages 9–12, A1+/A2. Three potions practise irregular plurals and special plural forms. No registration, libraries, online fonts, audio, countdown, or database.

## Run

Open `index.html` directly in a browser. All game files work locally without a server or an internet connection. For local HTTP preview, use `python -m http.server 8000 --bind 127.0.0.1` from this directory and visit `http://127.0.0.1:8000/`.

## Files

- `index.html`: entry page.
- `style.css`: responsive layout, CSS illustration fallbacks and animations, including reduced motion.
- `layout.css`: one-room game scenes constrained to `100dvh`, the full-height witch, an independent cauldron and parchment cards directly over the laboratory background, with a separate phone layout.
- `start.css`: full-room start scene with the original witch, cauldron and laboratory PNGs, small wand sparks and idle bubbles. All rules are scoped to the introduction.
- `final.css`: viewport-sized celebration with the original happy witch, sequential single-to-group animal transformations, SVG wand trails, quiet ambient sparks and reduced-motion support.
- `failure.css`: local green-to-purple wrong-potion reaction and amber excess-ingredient warning, without changing the scene layout.
- `data.js`: all words, options, correct answers and potion results.
- `script.js`: rendering and game logic.
- `public/assets/witch-lab/`: optional PNG assets; see its README for the exact filenames.

No build or installation is required. To publish as a static site, copy the whole directory, preserving relative paths, including `public/`. It also works under a repository subpath.

## Play

1. Select six irregular plural nouns. Tap an ingredient again to remove it; desktop drag-and-drop into the cauldron also works. Brew only succeeds with the exact six-word set.
2. Choose ten plural forms, with shuffled questions and options. Wrong answers can be retried without advancing.
3. Judge twelve phrases using KEEP IT / FIX IT, then choose corrections where needed. Only correct decisions advance the recipe.

Brewing and accepted answers lock controls to prevent repeat credit. Results animate exactly 5 mice, 4 geese and 6 sheep, then unlock the next potion. PLAY AGAIN clears the run and shuffles the tasks and choices again. There are no saved student records.

## Verification

`python tests/check_game.py` uses Python Playwright and an installed Microsoft Edge for development checks only; the game itself has no dependencies. Start the local HTTP preview before running the suite. It covers complete desktop and touch/mobile runs with normal motion, offline `file://` launch with network disabled, incorrect answers, exact recipes, duplicate clicks, all 22 sequential tasks, exact animal counts at every reveal, supplied PNG loading, purple smoke, replay, reduced motion and 320px layout. Reports and screenshots are written to the ignored `work/` folder.

`python tests/check_final.py` completes the real game twice and checks the celebration timeline: one mouse becomes five, then one goose becomes four, then one sheep becomes six. Single and group PNGs never overlap. The title and replay button appear after the last transformation. It verifies six viewport sizes, caption/image separation, reduced motion and a fresh animation after replay. Celebration screenshots are saved under `work/final/`.

`python tests/check_failure.py` checks empty, excessive and six-word incorrect recipes on desktop and phones. It verifies the green bubbling, local purple POOF, muddy liquid, input lock, repeat attempts, retained selections, capped amber progress, reduced motion and successful correction. Screenshots are saved under `work/failure/`. There is no audio system, so the reaction is visual only.

Accepted answers use a CSS card flight from the clicked card to the cauldron. First-round selections all have the same effect to avoid giving away correctness. Brewing adds a soft green glow, small bubbles and a short purple smoke cloud over the supplied cauldron PNG. The original animal stays on screen while the remaining animals appear one at a time; group PNGs are reserved for the final summary. On phones, brewing brings the cauldron into view. Reduced motion skips card flight, smoke and animated reveals.

Card flight ends at the centre of the supplied cauldron PNG’s opening. In round 1, selected-word labels appear after the flight; selection state and checking rules remain immediate and unchanged. The witch PNG is shown in full without cropping. Artificial windows, shelves, illustration panels and ingredient panels are absent from all three rounds.

The 64px progress indicator uses three SVG cauldrons with completed, active and locked states. Each round groups its title, instruction, question, choices, local feedback and collected ingredients together. Question numbering is separate from accepted ingredient count; the bar animates from its previous fill after a correct answer arrives. The original illustration coordinates are retained on desktop.

`python tests/check_layout.py` plays all three rounds at 1280×720, 1366×768, 1440×900, 1920×1080, 390×844 and 320×740. It checks page overflow, clipped controls/images, readable word size, every selection density, every phrase/correction and the BREW buttons. Desktop rounds fit within a single viewport; small phones may scroll to preserve readability. The 1366×768 screenshots and layout report are saved under `work/layout/`.
