// Renders index.html to video frames with Playwright and pipes them to FFmpeg.
//   node render.mjs beats            a still every half beat (half second if no beat grid) + contact sheets
//   node render.mjs draft            30 fps, no motion blur            (out/draft.mp4)
//   node render.mjs final            60 fps, 4 subframes blended       (out/video.mp4)
//   node render.mjs frame 12.5 ...   single frames at the given beats  (out/frames)
import { chromium } from 'playwright';
import { spawn, execFileSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(dir, 'out');
const mode = process.argv[2] ?? 'draft';
mkdirSync(out, { recursive: true });

// The headless browser occasionally dies on long renders; open() is used again to recover.
let browser, page;
async function open() {
  try { await browser?.close(); } catch {}
  browser = await chromium.launch();
  page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => { console.error('PAGE ERROR', e.message); process.exitCode = 1; });
  await page.goto(pathToFileURL(path.join(dir, 'index.html')).href);
  await page.waitForFunction('window.ready === true');
}
await open();
const { duration, info, sfx } = await page.evaluate(() => ({ duration: window.DURATION, info: window.BEATINFO, sfx: window.SFX }));
writeFileSync(path.join(out, 'cues.json'), JSON.stringify({ duration, ...info, sfx }, null, 1));
const shot = async (t, opts) => {
  for (let attempt = 1; ; attempt++) {
    try { await page.evaluate((x) => window.seek(x), t); return await page.screenshot(opts); }
    catch (e) {
      if (attempt >= 4) throw e;
      console.error(`browser lost at t=${t.toFixed(3)} (${e.message.split('\n')[0]}); relaunching, attempt ${attempt + 1}`);
      await open();
    }
  }
};
const beatTime = (b) => info.PHASE + b * info.BEAT;

if (mode === 'beats' || mode === 'frame') {
  const sub = mode === 'beats' ? 'beats' : 'frames';
  mkdirSync(path.join(out, sub), { recursive: true });
  const beats = mode === 'beats'
    ? Array.from({ length: Math.ceil(info.BEATS + 4) * 2 }, (_, i) => i / 2)
    : process.argv.slice(3).map(Number);
  for (const [i, b] of beats.entries()) {
    const name = mode === 'beats' ? String(i).padStart(3, '0') : `b${b.toFixed(2)}`;
    await shot(beatTime(b), { path: path.join(out, sub, `${name}.png`) });
  }
  if (mode === 'beats') {
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '1', '-i', path.join(out, 'beats', '%03d.png'),
      '-vf', "scale=640:-1,drawtext=text='t=%{eif\\:n/2\\:d}.%{eif\\:mod(n\\,2)*5\\:d}':x=10:y=10:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6,tile=4x4",
      path.join(out, 'beats', 'sheet-%02d.jpg')]);
  }
  console.log(`${beats.length} frames → out/${sub}`);
} else {
  const final = mode === 'final';
  const fps = final ? 60 : 30, sub = final ? 4 : 1, shutter = 0.6;
  const frames = Math.round(duration * fps);
  const vf = sub > 1 ? ['-vf', `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/(${fps}*TB)`] : [];
  const file = path.join(out, final ? 'video.mp4' : 'draft.mp4');
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps * sub), '-c:v', 'mjpeg', '-i', '-',
    ...vf, '-r', String(fps), '-c:v', 'libx264', '-preset', final ? 'slow' : 'veryfast', '-crf', final ? '15' : '20',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = 0; f < frames; f++) {
    for (let k = 0; k < sub; k++) {
      const buf = await shot((f + (k / sub) * shutter) / fps, { type: 'jpeg', quality: 96 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    if (f % 120 === 0) console.log(`frame ${f}/${frames}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log(`${file}  ${frames} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
await browser.close();
