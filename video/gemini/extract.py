#!/usr/bin/env python3
"""Separa la placa de Gemini Travel (1080x1350) en capas PNG con transparencia.

Uso: python3 video/gemini/extract.py
Lee src/portada.webp y escribe layers/*.png + layers/layers.json (posición de cada capa
en coordenadas de la placa original).
"""
import json
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'layers')
os.makedirs(OUT, exist_ok=True)

src = np.asarray(Image.open(os.path.join(HERE, 'src', 'portada.webp')).convert('RGB')).astype(np.float32)
H, W = src.shape[:2]
CREAM = np.array([255, 252, 241], np.float32)
meta = {}


def poly_mask(pts, feather=0.8, rounded=None):
    """Máscara 0..1 de un polígono (o rect redondeado) con borde suave."""
    m = Image.new('L', (W * 4, H * 4), 0)
    d = ImageDraw.Draw(m)
    if rounded:
        x0, y0, x1, y1, r = rounded
        d.rounded_rectangle([x0 * 4, y0 * 4, x1 * 4, y1 * 4], r * 4, fill=255)
    else:
        d.polygon([(x * 4, y * 4) for x, y in pts], fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    if feather:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(m).astype(np.float32) / 255


def save(name, rgb, alpha, pad=2):
    ys, xs = np.where(alpha > 0.01)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, W)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, H)
    rgba = np.dstack([rgb, alpha * 255])[y0:y1, x0:x1]
    Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, name + '.png'))
    meta[name] = {'x': int(x0), 'y': int(y0), 'w': int(x1 - x0), 'h': int(y1 - y0)}


# ---------------------------------------------------------------- formas
phone = poly_mask(None, rounded=(291, 551, 802, 1420, 62))
aruba = poly_mask(None, rounded=(418, 1058, 662, 1420, 28))
samana = poly_mask([(197, 1185), (203, 1160), (225, 1149), (398, 1111), (414, 1118), (424, 1135),
                    (424, 1350), (241, 1350)])
natal = poly_mask([(655, 1108), (676, 1113), (862, 1148), (880, 1162), (887, 1185), (872, 1268),
                   (857, 1350), (655, 1350)])
bub1 = poly_mask(None, rounded=(706, 803, 1008, 871, 34))
bub2 = poly_mask(None, rounded=(416, 897, 1008, 966, 34))
bub3 = poly_mask(None, rounded=(836, 991, 1008, 1046, 27))
bubbles = np.maximum.reduce([bub1, bub2, bub3])
cards = np.maximum.reduce([aruba, samana, natal])

# Paneles de Ads Manager: blancos/grises sobre fondo azul saturado.
sat = src.max(2) - src.min(2)
light = (src.min(2) > 150) & (sat < 90)
dark_ui = src.max(2) < 120  # textos/íconos oscuros dentro del panel


def panel_mask(region_poly):
    reg = poly_mask(region_poly, feather=0) > 0.5
    m = ((light | dark_ui) & reg).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # rellenar agujeros (textos azules, toggles)
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    big = max(cnts, key=cv2.contourArea)
    hull = cv2.convexHull(big)
    out = np.zeros_like(m)
    cv2.fillPoly(out, [hull], 255)
    return cv2.GaussianBlur(out.astype(np.float32) / 255, (0, 0), 0.8)


panelL = panel_mask([(55, 1000), (300, 1000), (300, 1350), (55, 1350)])
# el borde superior derecho queda bajo la burbuja: recta medida en x=1015..1075
panelR = poly_mask([(790, 922), (1015, 877), (1080, 864), (1080, 1350), (790, 1350)])

# ---------------------------------------------------------------- fondo estimado
fg = np.maximum.reduce([phone, cards, bubbles, panelL, panelR])
fg[:420] = 1  # zona de títulos
for box in [(160, 525, 330, 690), (630, 440, 920, 600)]:  # logos Meta / Gemini
    fg[box[1]:box[3], box[0]:box[2]] = 1
fg = cv2.dilate((fg > 0.05).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(np.float32)
keep = 1 - fg
num = cv2.GaussianBlur(src * keep[..., None], (0, 0), 40)
den = cv2.GaussianBlur(keep, (0, 0), 40)[..., None] + 1e-4
bg = num / den
bg[:430] = CREAM  # arriba es crema plano
Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).save(os.path.join(OUT, '_bg_estimado.png'))

# ---------------------------------------------------------------- textos (key sobre crema)
BLACK = np.array([22, 22, 22], np.float32)
BLUE = np.array([20, 80, 245], np.float32)


def key_two(pix, bgc, colors):
    best_a, best_c, best_r = None, None, None
    for c in colors:
        d = bgc - c
        a = np.clip(((bgc - pix) * d).sum(-1) / (d * d).sum(), 0, 1)
        r = np.linalg.norm(bgc - a[..., None] * d - pix, axis=-1)
        if best_a is None:
            best_a, best_r = a, r
            best_c = np.broadcast_to(c, pix.shape).copy()
        else:
            sel = r < best_r
            best_a = np.where(sel, a, best_a)
            best_r = np.where(sel, r, best_r)
            best_c[sel] = c
    return best_a, best_c


top = src[:420]
ta, tc = key_two(top, CREAM, [BLACK, BLUE])
ta[ta < 0.04] = 0
# recolorear con el color real (desmultiplicado) para conservar matices
real = CREAM - (CREAM - top) / np.maximum(ta[..., None], 1e-3)
tc = np.where(ta[..., None] > 0.5, np.clip(real, 0, 255), tc)

# líneas: rumor / Sin redes. Un año después: / 2.428 consultas. / Gemini Travel. A menos...
lines = {'logo': (40, 110), 'l1': (130, 215), 'l2': (215, 315), 'l3': (322, 400)}
for name, (y0, y1) in lines.items():
    a = np.zeros((H, W), np.float32)
    rgb = np.zeros((H, W, 3), np.float32)
    a[y0:y1] = ta[y0:y1]
    rgb[y0:y1] = tc[y0:y1]
    if name == 'logo':
        save('t_logo', rgb, a)
        continue
    # partir en palabras por huecos de columnas
    cols = (a[y0:y1] > 0.15).any(0)
    xs = np.where(cols)[0]
    groups, start, prev = [], xs[0], xs[0]
    gap = 16 if name != 'l3' else 12
    for x in xs[1:]:
        if x - prev > gap:
            groups.append((start, prev))
            start = x
        prev = x
    groups.append((start, prev))
    for i, (gx0, gx1) in enumerate(groups):
        aa = np.zeros_like(a)
        aa[y0:y1, gx0 - 2:gx1 + 3] = a[y0:y1, gx0 - 2:gx1 + 3]
        save(f't_{name}_{i}', rgb, aa)

# ---------------------------------------------------------------- logos (key sobre fondo estimado)
hsv = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)


def key_sat(box, lo, hi, extra=None):
    """Key por saturación: los logos son saturados, el fondo detrás es pálido."""
    x0, y0, x1, y1 = box
    pix, b = src[y0:y1, x0:x1], bg[y0:y1, x0:x1]
    a = np.clip((hsv[y0:y1, x0:x1, 1] - lo) / (hi - lo), 0, 1)
    if extra is not None:
        a = a * extra[y0:y1, x0:x1]
    real = b + (pix - b) / np.maximum(a[..., None], 1e-3)
    A = np.zeros((H, W), np.float32)
    R = np.zeros((H, W, 3), np.float32)
    A[y0:y1, x0:x1] = a
    R[y0:y1, x0:x1] = np.clip(real, 0, 255)
    return R, A


R, A = key_sat((160, 525, 330, 690), 95, 210, extra=1 - phone)
save('meta', R, A)
R, A = key_sat((628, 440, 925, 600), 30, 110)
gem_alpha = A
save('gemini', R, A)

# ---------------------------------------------------------------- teléfono
ph = src.copy()
# quitar burbujas de chat de la pantalla: inpaint
hole = ((np.maximum(bub1, bub2) > 0.02) | ((gem_alpha > 0.05) & (phone > 0.5) & (np.arange(H)[:, None] < 572))).astype(np.uint8) * 255
hole = cv2.dilate(hole, np.ones((5, 5), np.uint8))
ph8 = cv2.inpaint(ph.astype(np.uint8), hole, 9, cv2.INPAINT_TELEA).astype(np.float32)
# parte tapada por las placas: continuar el feed con fondo negro + inpaint suave
under = (cards > 0.02).astype(np.uint8) * 255
under = cv2.dilate(under, np.ones((7, 7), np.uint8)) & (phone > 0.5).astype(np.uint8) * 255
ph8b = cv2.inpaint(ph8.astype(np.uint8), under, 15, cv2.INPAINT_TELEA).astype(np.float32)
# oscurecer y desenfocar lo inventado para que no llame la atención
blurred = cv2.GaussianBlur(ph8b, (0, 0), 6) * 0.55
u = cv2.GaussianBlur(under.astype(np.float32) / 255, (0, 0), 4)[..., None]
ph8b = ph8b * (1 - u) + blurred * u
# el marco del teléfono sigue por debajo: pintar bisel gris en los bordes tapados
save('phone', ph8b, phone)

# ---------------------------------------------------------------- paneles
PANEL_FILL = np.array([246, 247, 250], np.float32)
for name, pm in (('panelL', panelL), ('panelR', panelR)):
    occl = np.maximum.reduce([phone, cards, bubbles])
    occl = cv2.dilate((occl > 0.02).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    occl = cv2.GaussianBlur(occl, (0, 0), 1.5)[..., None]
    rgb = src * (1 - occl) + PANEL_FILL * occl
    save(name, rgb, pm)

# ---------------------------------------------------------------- placas
for name, m in (('samana', samana), ('aruba', aruba), ('natal', natal)):
    rgb = src.copy()
    if name in ('samana', 'natal'):
        # lo que tapa Aruba: estirar el borde visible
        occl = (aruba > 0.02).astype(np.uint8) * 255
        occl = cv2.dilate(occl, np.ones((5, 5), np.uint8)) & (m > 0.02).astype(np.uint8) * 255
        rgb = cv2.inpaint(rgb.astype(np.uint8), occl, 7, cv2.INPAINT_TELEA).astype(np.float32)
    save(name, rgb, m)

with open(os.path.join(OUT, 'layers.json'), 'w') as f:
    json.dump(meta, f, indent=1)
print(json.dumps(meta))
