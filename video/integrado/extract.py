#!/usr/bin/env python3
"""Prepara las capas para la animación "Todo integrado".

- Los PNG que pasó el cliente (src/*.png) se ubican en la placa de referencia por template matching.
- Lo que falta (título, R, Medición, Samaná, Natal, burbujas de chat) se recorta de la referencia
  separándolo del fondo azul plano.
Salida: layers/*.png + layers/layers.json con x, y, w, h en coordenadas 1080x1920.
"""
import json
import os

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'layers')
os.makedirs(OUT, exist_ok=True)
ref = np.asarray(Image.open(os.path.join(HERE, 'src', 'referencia.webp')).convert('RGB')).astype(np.float32)
H, W = ref.shape[:2]
BLUE = np.array([0, 86, 255], np.float32)
dist = np.linalg.norm(ref - BLUE, axis=-1)
meta = {}


def save(name, rgba, x, y):
    Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, name + '.png'))
    meta[name] = {'x': int(x), 'y': int(y), 'w': int(rgba.shape[1]), 'h': int(rgba.shape[0])}


def crop_save(name, rgb, alpha, box):
    x0, y0, x1, y1 = box
    save(name, np.dstack([rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1] * 255]), x0, y0)


# ------------------------------------------------ PNG del cliente: ubicar en la referencia
def locate(fname, search=None):
    im = np.asarray(Image.open(os.path.join(HERE, 'src', fname)).convert('RGBA')).astype(np.float32)
    a = im[..., 3:] / 255
    comp = im[..., :3] * a + BLUE * (1 - a)
    hay = ref if search is None else ref[search[1]:search[3], search[0]:search[2]]
    res = cv2.matchTemplate(hay, comp, cv2.TM_SQDIFF)
    _, _, loc, _ = cv2.minMaxLoc(res)
    x, y = loc
    if search is not None:
        x, y = x + search[0], y + search[1]
    return im, x, y


for name, f, s in [('contenido', 'card-contenido.png', (0, 120, 520, 420)),
                   ('anuncios', 'card-anuncios.png', (360, 180, 820, 420)),
                   ('cursor', 'cursor.png', (560, 260, 800, 480)),
                   ('bajada', 'texto-bajada.png', (0, 780, 900, 960)),
                   ('aruba', 'promo-aruba.png', (250, 1330, 820, 1920))]:
    im, x, y = locate(f, s)
    save(name, im, x, y)

ar = meta['aruba']
aruba_mask = np.zeros((H, W), np.float32)
aruba_full = np.asarray(Image.open(os.path.join(HERE, 'src', 'promo-aruba.png')))[..., 3] / 255
y1 = min(ar['y'] + ar['h'], H)
aruba_mask[ar['y']:y1, ar['x']:ar['x'] + ar['w']] = aruba_full[:y1 - ar['y']]


# ------------------------------------------------ textos oscuros / claros sobre azul
def key_color(fg):
    d = BLUE - fg
    a = np.clip(((BLUE - ref) * d).sum(-1) / (d * d).sum(), 0, 1)
    return np.broadcast_to(fg, ref.shape).astype(np.float32), a


INK = np.array([17, 17, 17], np.float32)
rgb, a = key_color(INK)
crop_save('titulo1', rgb, a, (60, 576, 822, 690))
a2 = a.copy()
a2[:686] = 0
a2[:690, 505:580] = 0  # el palito de la 'g' de integrado baja hasta 687
crop_save('titulo2', rgb, a2, (80, 684, 900, 776))

CREAM = np.array([255, 252, 241], np.float32)
rgb, a = key_color(CREAM)
crop_save('r', rgb, a, (60, 1020, 256, 1256))


# ------------------------------------------------ card Medición (blanca con texto negro y halo)
def key_two(region, colors):
    x0, y0, x1, y1 = region
    pix = ref[y0:y1, x0:x1]
    best = None
    for c in colors:
        d = BLUE - c
        al = np.clip(((BLUE - pix) * d).sum(-1) / (d * d).sum(), 0, 1)
        r = np.linalg.norm(BLUE - al[..., None] * d - pix, axis=-1)
        if best is None:
            best = [al, r]
        else:
            sel = r < best[1]
            best[0] = np.where(sel, al, best[0])
            best[1] = np.where(sel, r, best[1])
    al = best[0]
    real = BLUE + (pix - BLUE) / np.maximum(al[..., None], 1e-3)
    return np.clip(real, 0, 255), al


box = (40, 330, 520, 480)
rgb, al = key_two(box, [np.array([255, 255, 250], np.float32), INK])
# no tomar el borde inferior de la card Anuncios
an = meta['anuncios']
yy, xx = np.mgrid[box[1]:box[3], box[0]:box[2]]
al = np.where((xx > 420) & (yy < 352), 0, al)
save('medicion', np.dstack([rgb, al * 255]), box[0], box[1])


# ------------------------------------------------ promos Samaná y Natal (fotos opacas)
def photo_layer(name, region):
    x0, y0, x1, y1 = region
    m = ((dist > 45) & (aruba_mask < 0.5)).astype(np.uint8)
    reg = np.zeros_like(m)
    reg[y0:y1, x0:x1] = 1
    m = m * reg
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    big = max(cnts, key=cv2.contourArea)
    hard = np.zeros_like(m)
    cv2.fillPoly(hard, [big], 1)
    inner = cv2.erode(hard, np.ones((5, 5), np.uint8)).astype(np.float32)
    soft = np.clip((dist - 20) / 120, 0, 1) * cv2.dilate(hard, np.ones((3, 3), np.uint8))
    alpha = np.maximum(inner, soft)
    # la parte tapada por Aruba: extender con el píxel vecino (queda siempre detrás de Aruba)
    under = ((aruba_mask > 0.02) & (reg > 0)).astype(np.uint8)
    rgb = ref.copy()
    fill = cv2.inpaint(rgb.astype(np.uint8), (under * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)
    rgb = fill.astype(np.float32)
    # Aruba tapa una franja de la card: rellenar con alfa 1 hasta el borde de Aruba
    ys, xs = np.where(hard)
    alpha = np.where((under > 0) & (cv2.dilate(hard, np.ones((25, 25), np.uint8)) > 0), 1, alpha)
    real = BLUE + (rgb - BLUE) / np.maximum(alpha[..., None], 1e-3)
    rgb = np.where(alpha[..., None] < 0.999, np.clip(real, 0, 255), rgb)
    ys, xs = np.where(alpha > 0.01)
    crop_save(name, rgb, alpha, (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


photo_layer('samana', (0, 1440, 420, 1920))
photo_layer('natal', (690, 1440, 1080, 1920))


# ------------------------------------------------ burbujas de chat (opacas, bordes redondeados)
def bubble(name, box, wipe_dots=False):
    x0, y0, x1, y1 = box
    al = np.clip((dist - 15) / 60, 0, 1)
    rgb = ref.copy()
    if wipe_dots:
        sub = rgb[y0:y1, x0:x1]
        navy = np.median(sub[(sub.sum(-1) < 200)], axis=0)
        bright = sub.sum(-1) > 300
        bright = cv2.dilate(bright.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        inner = np.zeros_like(bright)
        inner[8:-8, 20:-20] = True
        sub[bright & inner] = navy
        rgb[y0:y1, x0:x1] = sub
        meta_navy = [int(v) for v in navy]
        meta.setdefault('_colors', {})['navy'] = meta_navy
    crop_save(name, rgb, al, (x0 - 2, y0 - 2, x1 + 2, y1 + 2))


bubble('chat1', (700, 1087, 1000, 1154))
bubble('chat2', (412, 1181, 1000, 1248))
bubble('chat3', (829, 1274, 1000, 1342), wipe_dots=True)

# posición de los tres puntos
sub = ref[1274:1342, 829:1000]
pts = (sub.sum(-1) > 600).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(pts)
dots = [[float(cx + 829), float(cy + 1274), float(max(s[2], s[3]))] for s, (cx, cy) in zip(st[1:], cen[1:]) if s[4] > 30]
meta['_dots'] = sorted(dots)



# ------------------------------------------------ partir títulos en palabras y bajada en líneas
def split_words(name, gap):
    im = np.asarray(Image.open(os.path.join(OUT, name + '.png'))).astype(np.float32)
    cols = np.where((im[..., 3] > 40).any(0))[0]
    groups, start, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > gap:
            groups.append((start, prev)); start = c
        prev = c
    groups.append((start, prev))
    m = meta[name]
    for i, (g0, g1) in enumerate(groups):
        a, b = max(g0 - 3, 0), min(g1 + 4, im.shape[1])
        save(f'{name}_w{i}', im[:, a:b], m['x'] + a, m['y'])


split_words('titulo1', 14)
split_words('titulo2', 18)
bj = np.asarray(Image.open(os.path.join(HERE, 'src', 'texto-bajada.png'))).astype(np.float32)
rows = (bj[..., 3] > 30).any(1)
cut = 30 + int(np.argmin(rows[30:50].astype(int) + np.abs(np.arange(30, 50) - 38) * 0.01))
save('bajada_l0', bj[:cut], meta['bajada']['x'], meta['bajada']['y'])
save('bajada_l1', bj[cut:], meta['bajada']['x'], meta['bajada']['y'] + cut)

with open(os.path.join(OUT, 'layers.json'), 'w') as f:
    json.dump(meta, f, indent=1)
print(json.dumps(meta))
with open(os.path.join(OUT, 'layers.js'), 'w') as f:
    f.write('window.LAYERS = ' + json.dumps(meta) + ';\n')
