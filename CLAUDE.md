# Strata Test Drive — notes for Claude

A realistic driving simulator in one HTML page, hosted on GitHub Pages:
https://exclusive2knight.github.io/Strata-Test-Drive/

## Layout

- `src/app_template.html` — **the game source**. All HTML, CSS and JS live here. Edit this, never `index.html`.
- `src/mesh_data.js` — built-in meshes, spliced in at `/*MESH_DATA*/`.
- `build.py` — builds `dev.html` (readable, for tests; not committed) from `src/`, then runs `tools/protect.py` to make the published builds: `index.html` (minified, site-locked to exclusive2knight.github.io; GitHub Pages serves it) and `dist/artifact.html` (minified, no lock; published to the private Claude artifact; not committed). Run `python3 build.py` after every edit.
- `LICENSE` — all rights reserved. Never publish a readable build.
- `models/<key>.json` — one file per car model, fetched on demand.
- `acc_out/*.json` — people, animals and accessories (rigid-part skinned characters with `anims`).
- `sounds/` — audio.
- `docs/CARS.md` — every car with its current data and research status. `docs/RESEARCH_PLAN.md` — what still needs research and the data formats.
- `tools/` — test and screenshot tools (see below). `tools/research/` holds the raw research JSON behind the drive-mode (`DMODES`) and suspension (`SUSR`) tables that are embedded in the template.

## Workflow for every change

1. Edit `src/app_template.html`.
2. `python3 build.py`, then syntax-check the game script:
   `python3 -c "import re;open('/tmp/c.js','w').write(max(re.findall(r'<script>(.*?)</script>',open('dev.html').read(),re.S),key=len))" && node --check /tmp/c.js`
3. Test (below). Look at screenshots for anything visual.
4. Release:
   - Add a changelog entry: in the "What's new" panel, the newest version gets an `<h2>Version N · title</h2>` header, and the previous header becomes `<h4 class="old">…</h4>` inside the same `.nb` block.
   - Bump `const APP_VER="N"` (this resets players' saved games; that's expected).
   - Commit and push to `main`. GitHub Pages updates the site in a minute or two.
5. Write changelog text in plain, specific words for a player (what changed and what they'll notice).

## Testing

- `sh tools/serve.sh` serves the repo at http://127.0.0.1:8765 (the tools load `dev.html`; the locked `index.html` refuses to run on localhost) (needs Python; Playwright + Chromium for the tools).
- `python3 tools/run.py tools/tests/<test>.js` runs a JS test in headless Chromium. `tests/h.js` gives `SIM(seconds, fn)` / `SIMSTEP(dt)` to step the game without rendering, and a `hits` crash counter.
  - `t_all.js` driver assists (ACC, Pilot, LKA, AEB, BSM) · `tai.js` 5-minute AI traffic (overlaps / stuck) · `tfw.js` freeway and overpasses · `tgr.js` grass poking through roads (should be 0) · `pa1-5.js` park assist in the garage, lots, parallel, chargers · `thill.js` proving-ground hills and rails · `tev.js` plug-in battery modes · `tstab.js` suspension roll/ride per car · `tcpu.js` per-frame CPU cost.
  - Long simulations are slow in headless Chromium: keep sims short (≤ 20 s) and run several tests in parallel.
- `tools/shots/` — screenshot scripts: `multi.py out_prefix '[["name","x,y,heading","yaw,pitch,dist",cam,"extraJS"],…]'`, `hud.py 0|1` (PC / phone HUD), `set.py tabs` (settings), `glstat.py scenario` (draw calls and triangles per frame).

## Things to know about the code

- World: road graph `EDGES`/`NODES`, `groundAt(x,y)` gives the drivable height (picks the floor nearest `GREF` in multi-level places), `collAdd` registers obstacles (`COLL_KEEP` keeps proving-ground colliders across `collReset`).
- Garage on Fort St is a 2-bay double-threaded helix: `GAR`, `garZ(bay,n,x)`, `garStalls()`.
- Car physics: `physics(dt)` — tyres, 4-corner suspension from `TRIMS[k].sus` (derived from `SUSR` by `susDerive`), anti-roll sized from a target roll gradient. Drive modes: `DMODES` → `dmApply()`; EV / battery modes `T.eModes`.
- AI traffic: `updateTraffic`, IDM following, `aiVsPlayer` (horn, high beams, passing, brake checks), `aiSusp`.
- Rendering: big static meshes are tiled and frustum/distance culled (`meshChunked`, `CULL`); graphics tiers in `GQ` (lowest/low/medium/high) with an fps cap.
- The game also runs as a Claude artifact; `window.claude` multiplayer code is skipped when it isn't available, so the GitHub version just has no online players.
