/* Rumor · Landing 2026 */
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp01 = x => Math.max(0, Math.min(1, x));
const ease = x => 1 - Math.pow(1 - x, 3);
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

/* Mensajes flotantes del hero: logros reales de Rumor y sus clientes.
   Editar / sumar acá (label = encabezado chico, text = dato, sub = contexto). */
const HERO_MESSAGES = [
  { label: 'Caso Finteem', text: 'Escalado 4x en 12 meses', sub: 'Fintech · Finance partner' },
  { label: 'Recomendación', text: '82% de los nuevos clientes llegan por referidos', sub: 'Rumor · 2026' },
  { label: 'Caso Finteem', text: '+15M€ en flujo financiero analizado', sub: 'Dashboard activo' },
  { label: 'Clientes', text: '+60 marcas en Argentina y el exterior', sub: 'Turismo · B2B · Inmobiliaria' },
  { label: 'Caso Finteem', text: '+40 negocios acompañados', sub: 'Fintech · Finance partner' },
  { label: 'Medición', text: '100% de proyectos con dashboard activo', sub: 'Métricas reales, no de vanidad' },
];

/* ================= Fondo vivo (WebGL) =================
   Misma niebla del video vertical de servicios, adaptada a horizontal y sin textos. */
const VS = 'attribute vec2 p; void main(){ gl_Position = vec4(p,0.,1.); }';
const FS = `
precision highp float;
uniform vec2 res; uniform float t; uniform float mode;
vec3 hex(float r,float g,float b){ return vec3(r,g,b)/255.; }
float h(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float n(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h(i),h(i+vec2(1,0)),f.x), mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x), f.y); }
float fbm(vec2 p){ float v=0., a=.5; mat2 m=mat2(1.6,1.2,-1.2,1.6);
  for(int i=0;i<4;i++){ v+=a*n(p); p=m*p; a*=.5; } return v; }
void main(){
  vec2 uv = gl_FragCoord.xy/res;
  vec2 p = vec2(uv.x*res.x/res.y, uv.y)*1.5;
  float s = t*.09;
  vec2 q = vec2(fbm(p+vec2(0.,s)), fbm(p+vec2(5.2,1.3)-s*.7));
  vec2 r = vec2(fbm(p+3.*q+vec2(1.7,9.2)+s*.9), fbm(p+3.*q+vec2(8.3,2.8)-s*.6));
  float w = fbm(p+2.5*r);

  vec3 cream = hex(255.,252.,241.);
  vec3 mist  = hex(150.,152.,170.);
  vec3 black = hex(20.,20.,22.);
  vec3 blue  = hex(0.,58.,254.);
  vec3 blue2 = hex(0.,87.,255.);
  vec3 deep  = hex(5.,30.,254.);
  vec3 c;

  if (mode < .5) {
    // hero (modo claro): crema dominante, niebla azul que fluye desde abajo a la derecha
    float y = uv.y*.75 + (1.-uv.x)*.45 + (w-.5)*.6 + .04*sin(t*.3+uv.x*3.);
    c = cream;
    c = mix(c, hex(226.,232.,255.), smoothstep(.98,.62,y));
    c = mix(c, hex(150.,175.,255.), smoothstep(.72,.42,y)*.85);
    c = mix(c, blue2, smoothstep(.52,.22,y));
    c = mix(c, blue,  smoothstep(.30,.02,y));
    float g = smoothstep(.5,.0,length((uv-vec2(.82+.08*sin(t*.3),.78+.06*cos(t*.25)))*vec2(1.,1.4)));
    c = mix(c, hex(205.,216.,255.), g*.55);
    c += (r.x-.5)*.05;
    c += (h(gl_FragCoord.xy + fract(t*24.)*91.7) - .5)*.035;
    gl_FragColor = vec4(clamp(c,0.,1.),1.);
    return;
  } else if (mode > 1.5) {
    // reel (oscuro): azul abajo-derecha, humo negro al centro, niebla arriba
    float y = uv.y*.85 + (1.-uv.x)*.25 + (w-.5)*.5 + .05*sin(t*.3+uv.x*3.);
    c = blue2;
    c = mix(c, deep,  smoothstep(.05,.30,y));
    c = mix(c, blue,  smoothstep(.22,.40,y));
    c = mix(c, black, smoothstep(.40,.66,y));
    c = mix(c, mist,  smoothstep(.78,1.05,y)*.8);
    float g = smoothstep(.6,.0,length((uv-vec2(.78+.1*sin(t*.3),.3+.08*cos(t*.25)))*vec2(1.,1.5)));
    c = mix(c, blue2*1.15, g*.45);
  } else {
    // contacto: campo azul con humo negro y destellos crema
    c = mix(blue, deep, smoothstep(.3,.7,w));
    c = mix(c, black, smoothstep(.55,.85,w+r.y*.3)*.75);
    c = mix(c, blue2*1.1, smoothstep(.6,.0,length(uv-vec2(.5+.2*sin(t*.2),.5)))*.4);
    c = mix(c, mist, smoothstep(.72,.95,r.x)*.35);
  }
  c += (r.x-.5)*.06;
  float v = smoothstep(1.3,.35,length((uv-.5)*vec2(.9,1.1)));
  c *= mix(.7,1.,v);
  c += (h(gl_FragCoord.xy + fract(t*24.)*91.7) - .5)*.07;
  gl_FragColor = vec4(clamp(c,0.,1.),1.);
}`;

function fxBg(canvas) {
  const gl = canvas.getContext('webgl', { antialias: false, alpha: false });
  if (!gl) { canvas.style.background = 'radial-gradient(80% 80% at 80% 80%, #0057ff, #003afe 30%, #191919 70%)'; return; }
  const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; };
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
  gl.linkProgram(prog); gl.useProgram(prog);
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'p'); gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const uRes = gl.getUniformLocation(prog, 'res'), uT = gl.getUniformLocation(prog, 't');
  gl.uniform1f(gl.getUniformLocation(prog, 'mode'), { hero: 0, talk: 1, reel: 2 }[canvas.dataset.variant] ?? 0);

  // Render a media resolución: es niebla, no necesita nitidez y ahorra GPU
  const resize = () => {
    const k = Math.min(devicePixelRatio, 1.5) * .5;
    canvas.width = Math.max(2, canvas.clientWidth * k | 0);
    canvas.height = Math.max(2, canvas.clientHeight * k | 0);
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(uRes, canvas.width, canvas.height);
  };
  const draw = t => { gl.uniform1f(uT, t); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); };
  new ResizeObserver(() => { resize(); draw(4); }).observe(canvas);
  resize();
  loopWhenVisible(canvas, t => draw(t + 4));
}

/* Corre un loop rAF solo mientras el elemento está en pantalla.
   t = segundos desde que el elemento entró en pantalla (cada vez que vuelve a verse, arranca de cero). */
function loopWhenVisible(el, fn) {
  if (reduce) { fn(4); return; }
  let raf = 0, on = false, t0 = 0;
  const tick = () => { fn((performance.now() - t0) / 1000); raf = requestAnimationFrame(tick); };
  new IntersectionObserver(([e]) => {
    if (e.isIntersecting && !on) { on = true; t0 = performance.now(); tick(); }
    else if (!e.isIntersecting && on) { on = false; cancelAnimationFrame(raf); }
  }).observe(el);
}

/* ================= Cinta de luz del hero ================= */
function fxRibbon(canvas) {
  const ctx = canvas.getContext('2d');
  let W = 0, H = 0;
  const resize = () => { const k = .5; W = canvas.width = canvas.clientWidth * k | 0; H = canvas.height = canvas.clientHeight * k | 0; };
  new ResizeObserver(resize).observe(canvas); resize();
  const pts = t => {
    const out = [], N = 260;
    for (let i = 0; i <= N; i++) {
      const a = i / N * Math.PI * 2 * 1.35 + t * .15;
      out.push([
        W * .62 + Math.sin(a + .6) * W * .40 + Math.sin(a * 2.3 + t * .4) * W * .04,
        H * .48 + Math.sin(a * 2 + t * .12) * H * .30 + Math.cos(a * .7) * H * .1,
      ]);
    }
    return out;
  };
  const stroke = (p, to) => {
    ctx.beginPath();
    const b = Math.floor(to * (p.length - 1));
    for (let i = 0; i <= b; i++) i ? ctx.lineTo(p[i][0], p[i][1]) : ctx.moveTo(p[i][0], p[i][1]);
    ctx.stroke();
  };
  loopWhenVisible(canvas, t => {
    ctx.clearRect(0, 0, W, H);
    const p = pts(t), d = reduce ? 1 : ease(clamp01(t / 3));
    ctx.lineCap = ctx.lineJoin = 'round';
    const g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, 'rgba(0,58,254,1)'); g.addColorStop(.5, 'rgba(125,155,255,1)'); g.addColorStop(1, 'rgba(0,87,255,1)');
    ctx.strokeStyle = g;
    ctx.globalAlpha = .35; ctx.lineWidth = 16; ctx.filter = 'blur(12px)'; stroke(p, d);
    ctx.globalAlpha = .5; ctx.lineWidth = 4; ctx.filter = 'blur(2.5px)'; stroke(p, d);
    ctx.globalAlpha = .45; ctx.lineWidth = 1; ctx.filter = 'none'; stroke(p, d);
  });
}

/* Liquid glass: la deformación con filtro SVG sobre el fondo solo es estable en Chrome/Edge;
   el resto de los navegadores muestra el vidrio esmerilado sin deformar. */
if (/Chrome\//.test(navigator.userAgent) && !/CriOS|EdgiOS|FxiOS/.test(navigator.userAgent)) document.documentElement.classList.add('lg-on');

/* Mapa de la lente: el centro queda quieto y los bordes curvan el fondo, como el vidrio de Apple.
   Se genera una vez (canal R = desplazamiento X, G = desplazamiento Y). */
(function lensMap() {
  const fe = document.getElementById('lgLensMap');
  if (!fe) return;
  const N = 128, band = .3, c = document.createElement('canvas');
  c.width = c.height = N;
  const ctx = c.getContext('2d'), img = ctx.createImageData(N, N);
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const u = (i + .5) / N * 2 - 1, v = (j + .5) / N * 2 - 1;
    const ex = Math.max(0, Math.abs(u) - (1 - band)) / band, ey = Math.max(0, Math.abs(v) - (1 - band)) / band;
    const e = Math.min(1, Math.hypot(ex, ey)), m = e * e * (3 - 2 * e), len = Math.hypot(ex, ey) || 1;
    const o = (j * N + i) * 4;
    img.data[o] = 128 + Math.sign(u) * ex / len * m * 127;
    img.data[o + 1] = 128 + Math.sign(v) * ey / len * m * 127;
    img.data[o + 2] = 128; img.data[o + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  fe.setAttribute('href', c.toDataURL());
})();

/* Brillo del vidrio que sigue al mouse (solo actualiza dos variables CSS) */
addEventListener('pointermove', e => {
  const el = e.target.closest?.('.lg');
  if (!el || el.classList.contains('nav')) return;
  const r = el.getBoundingClientRect();
  el.style.setProperty('--mx', (e.clientX - r.left) / r.width * 100 + '%');
  el.style.setProperty('--my', (e.clientY - r.top) / r.height * 100 + '%');
}, { passive: true });

$$('.fx-bg').forEach(fxBg);
$$('.fx-ribbon').forEach(fxRibbon);

/* ================= Mensajes flotantes ================= */
(function chips() {
  const slots = $$('.chip-slot');
  let next = 0;
  const make = m => {
    const el = document.createElement('div');
    el.className = 'chip lg';
    el.innerHTML = `<span class="chip-ico"><img src="assets/isotipo-blanco.svg" alt=""></span>
      <div><small>${m.label}</small><b>${m.text}</b><span class="sub">${m.sub}</span></div>`;
    return el;
  };
  const show = slot => {
    const old = slot.firstElementChild;
    if (old) { old.classList.remove('on'); setTimeout(() => old.remove(), 900); }
    const el = make(HERO_MESSAGES[next++ % HERO_MESSAGES.length]);
    slot.appendChild(el);
    requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('on')));
  };
  const visible = () => slots.filter(s => s.offsetParent !== null);
  visible().forEach((s, i) => setTimeout(() => show(s), 900 + i * 700));
  if (reduce) return;
  let k = 0;
  setInterval(() => { const v = visible(); if (v.length) show(v[k++ % v.length]); }, 2600);
})();

/* ================= Reveal al hacer scroll ================= */
const io = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
}), { threshold: .15, rootMargin: '0px 0px -8% 0px' });
$$('.rv, .pack').forEach(el => io.observe(el));
requestAnimationFrame(() => $$('.hero .rv').forEach((el, i) => setTimeout(() => el.classList.add('in'), 150 + i * 140)));

/* ================= Scroll: nav, nosotros, reel, packs ================= */
const nav = $('#nav');
const about = $('.about'), glass = $$('.glass');
const reelFrame = $('#reelFrame');
const packs = $$('.pack');

function onScroll() {
  const vh = innerHeight;
  nav.classList.toggle('scrolled', scrollY > 40);
  const under = document.elementsFromPoint(innerWidth / 2, nav.offsetHeight / 2).find(el => !nav.contains(el));
  nav.classList.toggle('on-dark', !!under?.closest('.dark'));

  // Nosotros: las tres cards aparecen juntas cuando la sección entra en pantalla
  const on = about.getBoundingClientRect().top < vh * .45;
  glass.forEach(g => g.classList.toggle('on', on));

  // Reel: el marco se expande al entrar en pantalla
  const rr = reelFrame.getBoundingClientRect();
  const k = ease(clamp01((vh - rr.top) / (vh * .9)));
  reelFrame.style.width = (innerWidth < 760 ? 92 : 82) + k * (innerWidth < 760 ? 8 : 18) + '%';
  reelFrame.style.borderRadius = 32 - k * 32 + 'px';

  // Packs: la card de atrás se achica cuando la siguiente se apila encima
  packs.forEach((pk, i) => {
    const nx = packs[i + 1];
    const cs = getComputedStyle(pk);
    if (!nx || cs.position !== 'sticky') { pk.style.transform = ''; return; }
    const top = parseFloat(cs.top);
    const d = clamp01(1 - (nx.getBoundingClientRect().top - top) / vh);
    pk.style.transform = `scale(${1 - d * .06})`;
  });
}
addEventListener('scroll', () => requestAnimationFrame(onScroll), { passive: true });
addEventListener('resize', onScroll);
onScroll();

/* ================= Reel ================= */
(function reel() {
  const v = $('#reelVideo'), ph = $('#reelPh'), btn = $('#reelSound');
  btn.hidden = true;
  v.addEventListener('loadeddata', () => { ph.classList.add('hide'); btn.hidden = false; });
  new IntersectionObserver(([e]) => {
    if (!v.readyState) return;
    e.isIntersecting ? v.play().catch(() => {}) : v.pause();
  }, { threshold: .3 }).observe(v);
  v.addEventListener('canplay', () => v.play().catch(() => {}), { once: true });
  btn.addEventListener('click', () => { v.muted = !v.muted; btn.textContent = v.muted ? 'Sonido off' : 'Sonido on'; });
})();

/* ================= Flujo "cómo trabajamos" ================= */
(function flow() {
  if (!$('#flow')) return; // el bloque vive en bloques/como-trabajamos.html hasta que tenga su página
  const steps = $$('#flow .flow-steps li'), res = $('#flowResult'), st = $('#flowStatus');
  if (reduce) { steps.forEach(s => s.classList.add('done')); res.classList.add('on'); st.textContent = 'Completado'; st.classList.add('done'); return; }
  let i = -1, timer = 0, running = false;
  const reset = () => { steps.forEach(s => s.className = ''); res.classList.remove('on'); st.textContent = 'En curso'; st.classList.remove('done'); i = -1; };
  const step = () => {
    if (i >= 0 && i < steps.length) steps[i].className = 'done';
    i++;
    if (i < steps.length) { steps[i].className = 'active'; timer = setTimeout(step, 1300); }
    else { res.classList.add('on'); st.textContent = 'Completado'; st.classList.add('done'); timer = setTimeout(() => { reset(); step(); }, 4200); }
  };
  new IntersectionObserver(([e]) => {
    if (e.isIntersecting && !running) { running = true; reset(); timer = setTimeout(step, 400); }
    else if (!e.isIntersecting && running) { running = false; clearTimeout(timer); }
  }, { threshold: .35 }).observe($('#flow'));
})();

/* ================= Acelerador: curva de lanzamiento animada ================= */
(function launch() {
  const box = $('#launch');
  if (!box) return;
  const line = $('#launchLine'), clip = $('#launchClipRect'), dot = $('#launchDot');
  const days = $('#launchDays'), pct = $('#launchPct'), goal = $('#launchGoal'), ms = $$('.ms', box);
  const L = line.getTotalLength(), CYCLE = 8, RUN = 5.5;
  const at = k => { const pt = line.getPointAtLength(L * k); return [pt.x / 4, pt.y / 2.6, pt.x]; }; // % del viewBox 400×260
  ms.forEach(m => { const [x, y] = at(+m.dataset.at); m.style.left = x + '%'; m.style.top = y + '%'; });
  const inOut = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  // La línea y el área se revelan juntas con el mismo recorte; el punto marca la punta.
  // Cada vez que la card vuelve a verse, el ciclo arranca de cero (D-30, 0%).
  let lastPct = -1;
  loopWhenVisible(box, t => {
    const k = reduce ? 1 : inOut(clamp01((t % CYCLE) / RUN));
    const [x, y, vx] = at(k);
    clip.setAttribute('width', vx);
    dot.style.left = x + '%'; dot.style.top = y + '%';
    const pc = Math.round(k * 100);
    if (pc !== lastPct) {
      lastPct = pc;
      pct.textContent = pc + '%';
      days.textContent = 'D-' + Math.round(30 * (1 - k));
      goal.classList.toggle('hit', pc === 100);
      ms.forEach(m => m.classList.toggle('on', k >= +m.dataset.at));
    }
  });
})();

/* ================= Cómo trabajamos: de ruido a estructura =================
   Las palabras llegan dispersas (data-x = desplazamiento en vw) y se alinean con el scroll.
   El recorrido se mide en "pasos" de scroll fijos (U ≈ 2 giros de rueda), no en % de la sección:
   0–1U se ordena el set A · 1.05–1.5U fundido al hombre · 1.1–2.1U se ordena el set B · 2.2U cierre.
   El avance sigue al scroll con un suavizado por tiempo, así no salta con cada giro de la rueda. */
(function words() {
  const sec = $('.words');
  if (!sec) return;
  const setA = $('.set-a'), setB = $('.set-b'), A = $$('.w', setA), Bw = $$('.w', setB);
  const phA = $('.ph-a'), phB = $('.ph-b'), end = $('.words-end');
  const STEPS = 2.6;            // largo total del bloque fijo, en U
  let U = 240;                  // px de scroll por set (se ajusta al alto de pantalla)
  const place = (ws, k) => ws.forEach(w => { w.style.transform = `translate3d(${+w.dataset.x * (1 - k)}vw,0,0)`; });
  const render = s => {
    const kA = ease(clamp01(s)), out = clamp01((s - 1.05) / .45), kB = ease(clamp01(s - 1.1));
    place(A, kA); place(Bw, kB);
    setA.style.opacity = 1 - out; setA.style.transform = `translateY(${-out * 6}vh)`;
    setB.style.opacity = out; setB.style.transform = `translateY(${(1 - out) * 6}vh)`;
    phB.style.opacity = out;
    phA.style.setProperty('--zoom', 1.06 - kA * .06);
    phB.style.setProperty('--zoom', 1.06 - kB * .06);
    end.classList.toggle('on', s > 2.2);
  };
  let target = 0, cur = -1, raf = 0, prev = 0;
  const tick = now => {
    const dt = Math.min(.05, (now - (prev || now)) / 1000);
    prev = now;
    cur = cur < 0 ? target : cur + (target - cur) * (1 - Math.exp(-dt / .14));
    if (Math.abs(target - cur) < .002) cur = target;
    render(cur);
    raf = cur !== target ? requestAnimationFrame(tick) : (prev = 0, 0);
  };
  const update = () => {
    target = reduce ? STEPS : Math.max(0, Math.min(STEPS, -sec.getBoundingClientRect().top / U));
    if (!raf) raf = requestAnimationFrame(tick);
  };
  const size = () => {
    U = Math.round(Math.min(320, Math.max(200, innerHeight * .28)));
    sec.style.height = innerHeight + STEPS * U + 'px';
  };
  // Que la palabra más larga entre en el ancho (por si la tipografía de respaldo es más ancha que la Myriad Condensed)
  const fit = () => [setA, setB].forEach(set => {
    set.style.fontSize = '';
    const max = Math.max(...$$('.w', set).map(w => w.offsetWidth)), room = innerWidth * .92;
    if (max > room) set.style.fontSize = parseFloat(getComputedStyle(set).fontSize) * room / max + 'px';
  });
  addEventListener('scroll', update, { passive: true });
  addEventListener('resize', () => { size(); fit(); update(); });
  document.fonts?.ready.then(fit);
  size(); fit(); update();
})();

/* ================= Acordeón de servicios ================= */
$$('#acc .acc-item').forEach(item => item.querySelector('button').addEventListener('click', () => {
  const open = item.classList.contains('open');
  $$('#acc .acc-item').forEach(x => x.classList.remove('open'));
  if (!open) item.classList.add('open');
}));

/* ================= Contadores del caso ================= */
const cio = new IntersectionObserver(es => es.forEach(e => {
  if (!e.isIntersecting) return;
  cio.unobserve(e.target);
  const el = e.target, to = +el.dataset.count, pre = el.dataset.prefix || '', suf = el.dataset.suffix || '';
  if (reduce) return;
  const t0 = performance.now();
  (function tick() {
    const k = ease(clamp01((performance.now() - t0) / 1600));
    el.textContent = pre + Math.round(to * k) + suf;
    if (k < 1) requestAnimationFrame(tick);
  })();
}), { threshold: .6 });
$$('[data-count]').forEach(el => cio.observe(el));

/* ================= Testimonios en video ================= */
(function lightbox() {
  const lb = $('#lightbox'), v = $('video', lb);
  const close = () => { v.pause(); v.removeAttribute('src'); lb.hidden = true; };
  $$('.t-card').forEach(c => c.addEventListener('click', () => {
    if (!c.dataset.video) return;
    v.src = c.dataset.video; lb.hidden = false; v.play().catch(() => {});
  }));
  $('.lb-close', lb).addEventListener('click', close);
  lb.addEventListener('click', e => { if (e.target === lb) close(); });
  addEventListener('keydown', e => { if (e.key === 'Escape' && !lb.hidden) close(); });
})();
