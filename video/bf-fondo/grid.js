/* Motor del fondo Black Friday (grilla booleana Rumor). Uso: var g = RumorGrid(canvas, {modo:'pleno'|'centro'}); g.draw(t0a1, intro) */
window.RumorGrid = function (canvas, opts) {
  'use strict';
  opts = opts || {}; var MODO = opts.modo || 'pleno';

  var C = { black: '#191919', blue: '#003AFE', blue2: '#0057FF', white: '#FFFCF1', red: '#E3262B' };
  var CYCLE = 12, STEPS = 144, INTRO = 1.4, WIPE = 0.22;
  var THEMES = [
    { block: C.blue,  onInk: C.white, onG: ['+'],       offInk: C.blue2, offG: '-',   offA: 0.55, thr: -0.02 },
    { block: C.white, onInk: C.black, onG: ['%', '50'], offInk: C.white, offG: 'dot', offA: 0.20, thr: 0.24 },
    { block: C.red,   onInk: C.black, onG: ['-'],       offInk: C.red,   offG: '+',   offA: 0.50, thr: 0.02 }
  ];
  var TAU = 6.283185307;
  function hash(a, b, c) {
    var h = (Math.imul(a, 374761393) + Math.imul(b, 668265263) + Math.imul(c, 1274126177)) | 0;
    h = Math.imul(h ^ (h >>> 13), 1274126177); h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  }
  function smooth(e0, e1, x) { x = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return x * x * (3 - 2 * x); }

  function drawGlyph(g, ctx, s, color) {
    ctx.fillStyle = color; ctx.strokeStyle = color;
    var t = Math.max(1, s * 0.12), L = s * 0.46;
    if (g === '+') { ctx.fillRect(-L / 2, -t / 2, L, t); ctx.fillRect(-t / 2, -L / 2, t, L); }
    else if (g === '-') { ctx.fillRect(-L / 2, -t / 2, L, t); }
    else if (g === 'dot') { ctx.beginPath(); ctx.arc(0, 0, s * 0.09, 0, TAU); ctx.fill(); }
    else if (g === '%') {
      var r = s * 0.1, o = s * 0.15;
      ctx.lineWidth = t * 0.8;
      ctx.beginPath(); ctx.arc(-o, -o, r, 0, TAU); ctx.stroke();
      ctx.beginPath(); ctx.arc(o, o, r, 0, TAU); ctx.stroke();
      ctx.lineWidth = t * 0.85;
      ctx.beginPath(); ctx.moveTo(L * 0.5, -L * 0.5); ctx.lineTo(-L * 0.5, L * 0.5); ctx.stroke();
    } else {
      ctx.font = '800 ' + Math.round(s * 0.5) + 'px ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(g, 0, s * 0.04);
    }
  }
  function sprite(px, block, g, ink) {
    var c = document.createElement('canvas'); c.width = c.height = px;
    var x = c.getContext('2d');
    if (block) { x.fillStyle = block; x.fillRect(0, 0, px, px); }
    x.translate(px / 2, px / 2); drawGlyph(g, x, px, ink);
    return c;
  }

  var ctx = canvas.getContext('2d', { alpha: false });
  var W = 1080, H = 1920;
  // Misma densidad que en el celular: ~22 celdas de ancho
  var cell = Math.round(W / 22);
  var cols = Math.ceil(W / cell), rows = Math.ceil(H / cell);
  var ox = (W - cols * cell) / 2, oy = (H - rows * cell) / 2;
  var sprites = THEMES.map(function (T) {
    return { on: T.onG.map(function (g) { return sprite(cell, T.block, g, T.onInk); }), off: sprite(cell, null, T.offG, T.offInk) };
  });

  var n = cols * rows, U = new Float32Array(n), WT = new Float32Array(n);
  for (var j = 0; j < rows; j++) for (var i = 0; i < cols; i++) {
    var k = j * cols + i;
    var xn = (ox + (i + 0.5) * cell) / W, yn = (oy + (j + 0.5) * cell) / H;
    U[k] = xn * 0.45 + yn * 0.55;                      // barrido diagonal (versión vertical)
    var w = 1;
    if (MODO === 'centro') {
      // óvalo central oscuro donde va el sujeto o el artefacto
      var dx = (xn - 0.5) / 0.42, dy = (yn - 0.5) / 0.33;
      w = smooth(0.75, 1.25, Math.sqrt(dx * dx + dy * dy));
    }
    WT[k] = w;
  }

  function field(i, j, t) {
    var p = TAU * t;
    return (Math.sin(0.21 * i + 0.13 * j + p + 1.3) +
            Math.sin(-0.12 * i + 0.29 * j - p + 0.4) +
            Math.sin(0.33 * i - 0.17 * j + p + 2.1) * 0.8 +
            Math.sin(0.06 * i + 0.09 * j - 2 * p + 0.7) * 0.9 +
            Math.sin(0.52 * i + 0.41 * j - p + 4.2) * 0.45) / 3.6;
  }

  function draw(t, intro) {
    var step = Math.round(t * STEPS) % STEPS;
    var nT = THEMES.length, seg = t * nT, cur = Math.floor(seg) % nT, local = seg - Math.floor(seg);
    var nxt = (cur + 1) % nT, wipeP = (local - (1 - WIPE)) / WIPE;
    ctx.globalAlpha = 1; ctx.fillStyle = C.black; ctx.fillRect(0, 0, W, H);
    for (var k = 0; k < n; k++) {
      var i = k % cols, j = (k / cols) | 0, w = WT[k], h = hash(i, j, step);
      var x = Math.round(ox + i * cell), y = Math.round(oy + j * cell);
      if (intro >= 0) {
        var appear = hash(i, j, 991);
        if (appear > intro) continue;
        if (intro - appear < 0.12) {
          ctx.globalAlpha = h < 0.5 ? 0.25 + 0.6 * w : THEMES[0].offA;
          ctx.drawImage(h < 0.5 ? sprites[0].on[0] : sprites[0].off, x, y);
          continue;
        }
      }
      var th = cur, edge = false;
      if (wipeP >= 0) {
        var front = wipeP * 1.3 - 0.15;
        var d = U[k] + (hash(i, j, 7) - 0.5) * 0.12 - front;
        if (d < 0) th = nxt;
        edge = d > -0.05 && d < 0.05;
      }
      var T = THEMES[th], S = sprites[th];
      var f = field(i, j, t) + (hash(i, j, 3) - 0.5) * 0.28;
      var thr = T.thr + (1 - w) * 1.1;
      var on = f > thr;
      if (edge && h < 0.45) on = !on;
      else if (Math.abs(f - thr) < 0.06 && h < 0.3) on = !on;
      if (w < 0.15) on = false;
      if (on) {
        ctx.globalAlpha = 1;
        ctx.drawImage(S.on[S.on.length > 1 ? (hash(i, j, 11) < 0.6 ? 0 : 1) : 0], x, y);
      } else {
        ctx.globalAlpha = T.offA * (0.35 + 0.65 * w);
        ctx.drawImage(S.off, x, y);
      }
    }
    ctx.globalAlpha = 1;
  }

  return { draw: draw, CYCLE: CYCLE, INTRO: INTRO, STEPS: STEPS, THEMES: THEMES,
    themeAt: function (t) { return Math.floor(t * THEMES.length) % THEMES.length; } };
};
