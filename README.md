# Witch's Potion Lab

Halloween interactive English grammar game by Mr. Foxy.

**[Play the game](https://kseniantonova.github.io/witchs-potion-lab/)**

Help the witch make three multiplying potions: find irregular plurals, choose the correct form, and keep or fix phrases. The results are 5 mice, 4 geese and 6 sheep. Includes animated brewing, a playful wrong-potion reaction and a magical finale.

- Desktop and touch-friendly mobile layouts; reduced-motion support.
- Original PNG illustrations, CSS/SVG effects and no external services.
- Plain HTML, CSS and JavaScript. No npm packages, Vite, registration or audio.

## Run and build

Open `index.html` to play offline, or serve this folder with `python -m http.server 8000`.

Run `python build.py` to validate relative asset paths and package the game in `dist/`. The build copies the original game files without changing them; Python 3.9+ is required. No dependency installation is needed.

## Deployment

Every push to `main` runs [.github/workflows/pages.yml](.github/workflows/pages.yml), builds `dist/`, and deploys it through GitHub Pages. All game assets use relative paths and work under `/witchs-potion-lab/`.

Development notes and browser checks: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). Screenshots, local settings, build output and secrets are excluded from Git.
