---
name: product-film
description: 'Make a short, beat-synced product video (launch film, feature intro, demo reel, motion-design promo) entirely in code: one HTML file whose every frame is a pure function of time, captured with Playwright and encoded with FFmpeg, cut to a music track with synthesized UI sounds. Big-type title cards, cursor-driven UI demos, a particle burst and a particle-to-logo finale. Use whenever the user asks for a product video, launch video, promo, explainer animation, motion graphics, "做产品视频", "宣传片", "介绍片", or shares a code-generated video and asks for something like it, even if they never say "HTML" or "render". For step-by-step tutorials, use guide-video instead.'
---

# Product film

A 25–45 second film that presents a product: a hook with a slammed number, one chapter per feature (title card → redrawn UI demo driven by a cursor), a particle burst on the music's lift, and a finale where a sphere of dots explodes and lands as the logo, then wordmark and tagline. Everything is cut to the beat.

`assets/template.html` is a complete, working film with placeholder brand and three demo types (a list with a status change, a create form that adds a row, a dashboard whose toggle retargets the chart). Copy it and adapt it; do not start from a blank page.

## What the user decides, and what you decide

Ask only for what you cannot find out: which product, which features matter most, who it is for, and the language of the on-screen text. Pick length, structure, copy and typography yourself and say what you picked. A user who says "you decide the rest" means it.

## Workflow

### 1. Learn the real product

Look at the actual project before inventing anything: design tokens (colours, radii, font weights), the logo SVG, existing screenshots, and the UI copy (i18n files are the fastest source of real labels, statuses and button text). A demo built from the product's own vocabulary reads as the product; one built from guesses reads as a template. Redraw the UI in HTML rather than recording the live app: it stays crisp at any zoom and every state is controllable. Never invent features or screens the product does not have.

### 2. Music first

The track decides the length and where the big moment goes, so settle it before storyboarding.

- A finished royalty-free track sounds fuller than anything synthesized here. Ask the user to pick one (steady electronic, 105–125 BPM, drums in within the first bars). Downloading a file needs the user's go-ahead; a file or URL they hand you for this is that go-ahead.
- Run `scripts/analyze_track.py <file>` (needs numpy and ffmpeg; if the default `python3` lacks numpy, find an interpreter that has it and use the same one for `sfx.py` and `mux.sh`). It prints tempo, the time of beat 0, grid drift, loudness per bar and the biggest lift. Autocorrelation often reports 2/3 of the true tempo; the script tries each octave and keeps the grid with the least drift — check the "other fits" line if the result looks odd.
- Put `bpm` and `phase` (beat 0) into `FILM`. Point `FILM.lift` at the chapter whose start is nearest the biggest lift.
- You cannot hear. Report measurements, never opinions about how it sounds, and ask the user to listen.

### 3. Storyboard on the beat grid

The template's layout, in beats: hook 0–8, chapter *i* at `8 + 8i`, finale at `8 + 8·chapters` lasting 8 beats, then a ~2 s tail. Three chapters is 40 beats (21 s at 114 BPM); five is 56. Choose a chapter count that ends on a phrase boundary of the track.

Something should change on every beat. Mix shot types — only UI demo feels like a screen recording, only type feels like a slideshow:

- **Hook** (beats 0–8): a plain line, a slammed giant number that counts up and reframes it, a one-line subtitle, then the product name line. Make sure the number is true and says what it counts (one customer's fleet is not the platform total).
- **Chapter**: index ("02 — 05"), a very large title, a subtitle, a faint outlined numeral; after 1.5 beats the title shrinks into a header and the hero card opens into the demo.
- **Demo**: the cursor performs the real interaction. Clicks land on beats; results appear on the following beats; a toast confirms.
- **Lift**: camera punch, ring and particle burst, preceded by a riser.
- **Finale**: sphere → explode → the dots land as the logo → wordmark → tagline → feature pills.

Show the user a beat-by-beat table when direction is still open; when they have approved the approach, build and show frames instead.

### 4. Build `index.html`

Set up a project folder (ask where; default `~/Downloads/<product>-video/`), copy `assets/template.html` to `index.html` and `scripts/*` next to it, and `npm i playwright` there (Node 18+).

Edit the `FILM` block (brand name, colours, logo SVG, hook, chapters, tagline, features), then replace the demo layers `D0, D1, …` with the product's screens and their scripts in `DEMO`. Each `DEMO[i]` works in beats from its chapter start `u` (the card is open from about u=1.6 to u=7.9):

- `cur: [[u, 'target']]` — cursor arrivals; targets are elements with `data-c="target"`, measured from the DOM at load. Each move starts 0.9 beat before it arrives.
- `clicks: [u]` — press beats (ripple + click sound). `toasts: [[u, 'text']]`. `keys: [[from, to, count]]` — typing ticks.
- `draw(u)` — sets every style of the layer from `u` alone.

Size each chapter's card with `w`, `h`, `r` and `zoom` so the demo fills the frame under the shrunken header. The logo SVG must be self-contained (no external images or fonts); the finale samples its pixels for the particles' targets and colours.

The contract the render script relies on:

```js
window.seek = t => render((t - PHASE) / BEAT)   // t in seconds; render() takes beats
window.DURATION                                  // seconds, including the tail
window.BEATINFO = { BPM, PHASE, BEAT, BEATS }
window.SFX = [{ t, k: 'click' | 'key' | 'ding' | 'impact' | 'slam' | 'whoosh' | 'riser', d? }]
window.ready = true                              // after fonts, logo sampling and measurement
```

Rules that keep it renderable and good-looking:

- **Everything is a pure function of time.** No CSS transitions or animations, no timers, no state carried between calls. Frames are captured out of order and several times each (motion-blur subframes), so anything stateful tears.
- **Springs are closed-form.** `spr(x, w, z)` is the step response of a damped spring. A value retargeted several times is `track(b, keys)`, the sum of one spring per change. Keep overshoot small (z ≈ 0.8–0.9).
- **One hero card morphs through the film**: it collapses into the gradient rule under each title, then opens into the next demo. Each demo layer has its own enter and exit window so two never overlap.
- **Seeded randomness only** (`rng(seed)`), so every render is identical.
- **Decorative, not functional, data**: obviously fake IDs and keys, QR-like patterns that do not scan.

Gotchas already paid for:

- Set `visibility: inherit`, not `visible`, when showing an element. A `visible` child shows through a hidden parent, and leftovers from other scenes appear as ghost text.
- Hide a layer even on beats where you skip its other updates; an early `return` before the hide leaves the last state on screen.
- Canvas `font` does not understand `-apple-system`; use `system-ui`.
- No `will-change` on anything that gets scaled, or its text renders blurry.
- Check a long number's font size at its final value, not its starting one.

### 5. Review frames before rendering video

`node render.mjs beats` writes one frame per half-beat plus 4×4 contact sheets in `out/beats/`. Read every sheet. Look for leftover elements, overlaps, cramped or cut-off text, cursors that miss their targets, and beats where nothing changes. `node render.mjs frame 12.5 34` renders single frames at full size. Fix and repeat until the sheets are clean — this loop is where the quality comes from.

### 6. Draft, then final

```bash
node render.mjs draft                                  # 30 fps, no blur, ~1 min
python3 sfx.py                                         # UI sounds from out/cues.json → out/sfx.wav
./mux.sh out/draft.mp4 audio/<track> out/<name>-draft.mp4
```

Send the draft straight away. Then run the final in the background (60 fps, 4 blended subframes; about 7–8 minutes for 35 s) and send it when it lands:

```bash
node render.mjs final && ./mux.sh out/video.mp4 audio/<track> out/<name>-final.mp4
```

The renderer relaunches the browser and retries a frame if headless Chromium dies mid-render. Before sending any file, check its modification time and pull a frame from it, so you never send a stale render.

## What to tell the user at the end

- You could not hear the mix; ask them to check sound-effect volume and tone.
- Which numbers, names and IDs are demo data, and where each came from (a headline number on a website is a claim).
- The UI is redrawn from the design, not recorded, so it will not match the live app pixel for pixel.
- Music licence terms are theirs to confirm before public use.

## Files

- `assets/template.html` — the complete film to copy: engine helpers, hero morph, chapters, three demo types, cursor, particles, finale, cue list.
- `scripts/analyze_track.py` — tempo, beat 0, drift, per-bar energy, biggest lift.
- `scripts/render.mjs` — `beats` | `frame <beat…>` | `draft` | `final`; writes `out/cues.json`.
- `scripts/sfx.py` — synthesizes clicks, key ticks, dings, impacts, whooshes and risers at the cue times.
- `scripts/mux.sh` — trims and fades the music, mixes in the sounds, muxes with the video.
