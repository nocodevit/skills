---
name: guide-video
description: Turn a step-by-step procedure into a polished tutorial video — onboarding guides, "how to integrate our API", setup walkthroughs, feature how-tos — built from real screenshots or redrawn UI, with a cursor that clicks through each step, highlighted regions, zooms, typed input, code that types itself and runs in a terminal, and a signature transition where tapping the next step's number in the corner expands into the next page. Renders an MP4 from one HTML file with Playwright and FFmpeg. Use whenever the user wants a tutorial video, a guide video, an onboarding or integration walkthrough, a screen-recording-style explainer, "教程视频", "接入指南视频", "操作步骤视频", or asks to turn steps, docs or screenshots into a video — even if they never mention HTML or rendering.
---

# Guide video

A tutorial video where each step is one page. The page opens with a big step number, a short title and one sentence; the right side shows the step itself — a screenshot in a browser frame, a code editor with a terminal, or a simple card. When the step is done, a round button with the next number pops up in the bottom-right corner, the cursor taps it, and the next page expands out of the button as a circle while the digit flies up to become the new page's number.

Everything is one `index.html` where every frame is a pure function of time. `scripts/render.mjs` captures it with Playwright; `scripts/sfx.py` and `scripts/mux.sh` add the sound.

## 1. Agree on the steps

Get from the user: the steps in order, who is watching (developers, customers, internal staff), and the language of the on-screen text. Rewrite each step as:

- **title** — an imperative phrase of at most about five words ("Create an API key").
- **desc** — one sentence the viewer can act on.
- **body** — what the viewer sees: `shot` (a screenshot), `code` (editor + terminal) or `card` (a small piece of HTML).
- **actions** — what happens on that body, in order.

Three to seven steps reads well. Merge or split steps until each one has a single clear outcome, and end with a `done: true` page that recaps them.

## 2. Collect screenshots

Real screenshots of the real product beat redrawn UI for tutorials, because viewers will look for exactly what they see in the video.

- Capture at a fixed viewport (1440×900 works well) with Playwright or the browser tool, one screenshot per state the viewer needs to see: before a click and after it.
- **Record coordinates while you capture.** Whenever you screenshot a state, also save `getBoundingClientRect()` of every element you will box, click or type into. Guessing pixel positions from a picture is how highlight boxes end up misaligned.
- Sign-in is the user's job. Ask them to log in themselves; never type a password. Creating real credentials (API keys, tokens, webhooks) is a change to their account — ask before doing it, and prefer a test or staging environment.
- Anything secret that appears (keys, tokens, emails, phone numbers, customer data) gets a `veil` action from the first frame, and you mention it in your report so the user can double-check.

## 3. Build the video

Set up a project folder (ask where; default `~/Downloads/<topic>-guide/`):

```bash
cp <skill>/assets/template.html index.html
cp <skill>/scripts/* .
npm init -y && npm pkg set type=module && npm i playwright    # Node 18+
mkdir shots    # screenshots go here, referenced as shots/<name>.png
```

Then replace the `CONTENT` block at the top of `index.html`: `THEME.pages` (one background and glow colour per page — neighbouring pages must differ, or the expanding circle is invisible) and `PAGES`.

### Actions on a `shot` page

Coordinates are in screenshot pixels.

| Action | Fields | What it does |
|---|---|---|
| `box` | `x y w h label?` | Draws a highlight rectangle with an optional tag above it. |
| `click` | `x y` | Moves the cursor there and clicks, with a ripple. |
| `type` | `x y w h text bg color? size?` | Types text into a field. `bg` should match the field so it covers any placeholder. |
| `zoom` | `x y w h` / none | Camera zooms so the region fills the frame; `{do:'zoom'}` alone zooms back out. |
| `swap` | `src` | Cross-fades to another screenshot (the state after a click). |
| `veil` | `x y w h from?` | Frosted-glass cover; `from:0` makes it present from the start. |
| `wait` | `s` | Pause. |

A `code` page takes `file`, `code`, `run` and `output`; the code types itself, the command runs with a spinner, and the output prints line by line (JSON is coloured).

Page length is computed from its content (typing speed, number of actions), so long steps hold longer automatically. Tune `INTRO`, `HOLD` and the `CPS_*` constants if the whole video feels rushed or slow.

## 4. Check frames before rendering video

```bash
node render.mjs frame 3 7.5 12        # full-size stills at those seconds → out/frames
node render.mjs beats                 # a still every 0.5 s plus contact sheets → out/beats
```

Look at every page after its content has settled and at every action: boxes sitting exactly on their targets, the cursor landing on what it clicks, typed text inside its field, nothing secret visible, nothing cut off by a zoom. Open `index.html?play` in a browser for a real-time preview.

## 5. Render

```bash
node render.mjs draft                          # 30 fps, quick look
node render.mjs final                          # 60 fps with motion blur
python3 sfx.py                                 # clicks, key ticks, the reveal "bubble" → out/sfx.wav  (needs numpy)
./mux.sh out/video.mp4 out/guide.mp4 [music] [volume]   # music is optional and sits low (default 0.25)
```

Send the draft as soon as it exists, then the final.

## Gotchas

- When showing an element, set `visibility: inherit`, not `visible`: a `visible` child shows through a hidden parent page.
- Canvas text needs `system-ui`, not `-apple-system`.
- Keep the page's title short; long titles wrap into the description (the description is placed under the title automatically, but four lines of title look heavy).
- Screenshots load asynchronously; the template waits for every `<img>` to decode before `window.ready`. A broken image path renders a blank window, so check the first frame of each shot page.

## What to tell the user at the end

- Which regions were veiled, so they can confirm nothing sensitive is visible.
- Which screenshots came from which environment (production, staging, local).
- That you cannot hear the mix — ask them to check the sound.
- Any UI that was redrawn rather than captured.

## Files

- `assets/template.html` — the engine plus placeholder content; replace the CONTENT block.
- `scripts/render.mjs` — `frame <seconds…>` | `beats` | `draft` | `final`; also writes `out/cues.json`.
- `scripts/sfx.py` — synthesizes the click, key and reveal sounds from the cues.
- `scripts/mux.sh` — puts the sounds (and optional music) under the video.
