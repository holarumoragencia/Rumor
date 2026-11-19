#!/usr/bin/env node
// Renderiza video/index.html cuadro a cuadro y arma un MP4 vertical 1080x1920.
// Uso: node video/integrado/render.cjs [--fps 30] [--out ...mp4] [--still 7]
// Además arma la pista de sonido con sfx.py a partir de window.SFX de la página.
const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');

let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, arr) =>
  a.startsWith('--') ? [...acc, [a.slice(2), arr[i + 1]]] : acc, []));
const FPS = Number(args.fps || 30);
const OUT = path.resolve(args.out || path.join(__dirname, 'out', 'todo-integrado.mp4'));
const FRAMES_DIR = path.join(__dirname, 'out', 'frames');

(async () => {
  const browser = await chromium.launch({
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('page error:', e); process.exit(1); });
  await page.goto('file://' + path.join(__dirname, 'index.html') + '?capture');
  await page.evaluate(() => document.fonts.ready);
  const stage = await page.$('#stage');

  if (args.still !== undefined) {
    fs.mkdirSync(path.dirname(OUT), { recursive: true });
    const t = Number(args.still);
    await page.evaluate(t => window.seek(t), t);
    const file = OUT.replace(/\.mp4$/, '') + `-still-${t}.png`;
    await stage.screenshot({ path: file });
    console.log(file);
    await browser.close();
    return;
  }

  const duration = await page.evaluate(() => window.DURATION);
  const cues = await page.evaluate(() => window.SFX || []);
  const CUES = path.join(__dirname, 'out', 'cues.json');
  const WAV = path.join(__dirname, 'out', 'sfx.wav');
  fs.mkdirSync(path.dirname(CUES), { recursive: true });
  fs.writeFileSync(CUES, JSON.stringify(cues));
  const a = spawnSync('python3', [path.join(__dirname, 'sfx.py'), CUES, WAV, String(duration)], { stdio: 'inherit' });
  if (a.status !== 0) process.exit(a.status);
  const total = Math.round(duration * FPS);
  fs.rmSync(FRAMES_DIR, { recursive: true, force: true });
  fs.mkdirSync(FRAMES_DIR, { recursive: true });
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => window.seek(t), f / FPS);
    await stage.screenshot({ path: path.join(FRAMES_DIR, `f${String(f).padStart(5, '0')}.png`) });
    if (f % FPS === 0) process.stdout.write(`\r${f}/${total}`);
  }
  await browser.close();
  console.log(`\r${total}/${total} cuadros`);

  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS),
    '-i', path.join(FRAMES_DIR, 'f%05d.png'), '-i', WAV,
    '-c:a', 'aac', '-b:a', '192k', '-shortest',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT],
    { stdio: 'inherit' });
  if (r.status !== 0) process.exit(r.status);
  fs.rmSync(FRAMES_DIR, { recursive: true, force: true });
  console.log(OUT);
})();
