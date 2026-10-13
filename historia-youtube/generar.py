"""Genera una historia 1080x1920 estilo "compartir en Spotify" a partir de una portada de YouTube."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PORTADA = os.path.join(AQUI, "portada.png")
SALIDA = os.path.join(AQUI, "historia.png")

TITULO = "Experto en finanzas: vender más ya no basta"
CANAL = "Finteem"
DURACION = "Video • 1 h 5 min"

S = 2  # supersampling para bordes suaves
W, H = 1080 * S, 1920 * S
F = "/usr/share/fonts/opentype/inter/"
def font(n, size): return ImageFont.truetype(F + n, size * S)

thumb = Image.open(PORTADA).convert("RGB")

# Colores derivados de la portada (como hace Spotify)
import colorsys

h = 0.42  # verde azulado de la portada
def tono(sat, val): return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, sat, val))
fondo = tono(0.55, 0.20)
tarjeta = tono(0.42, 0.34)

img = Image.new("RGB", (W, H), fondo)
d = ImageDraw.Draw(img)

# Tarjeta
cw = 900 * S
pad = 38 * S
tw = cw - 2 * pad
th = int(tw * thumb.height / thumb.width)
ch = pad + th + 40 * S + 120 * S + 64 * S + 46 * S + pad
cx, cy = (W - cw) // 2, (H - ch) // 2
d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=34 * S, fill=tarjeta)

# Portada con esquinas redondeadas
t = thumb.resize((tw, th), Image.LANCZOS)
m = Image.new("L", (tw, th), 0)
ImageDraw.Draw(m).rounded_rectangle([0, 0, tw, th], radius=18 * S, fill=255)
img.paste(t, (cx + pad, cy + pad), m)

# Avatar del canal (recorte circular de la cara en la portada)
av = 120 * S
fx0, fy0 = int(thumb.width * 0.60), int(thumb.height * 0.02)
side = int(thumb.height * 0.62)
cara = thumb.crop((fx0, fy0, fx0 + side, fy0 + side)).resize((av, av), Image.LANCZOS)
ma = Image.new("L", (av, av), 0)
ImageDraw.Draw(ma).ellipse([0, 0, av, av], fill=255)
ay = cy + pad + th + 40 * S
img.paste(cara, (cx + pad, ay), ma)

# Título (hasta 2 líneas) + canal
ft, fc = font("Inter-Bold.otf", 34), font("Inter-Medium.otf", 32)
tx = cx + pad + av + 28 * S
maxw = cx + cw - pad - tx
lineas, actual = [], ""
for p in TITULO.split():
    prueba = (actual + " " + p).strip()
    if d.textlength(prueba, font=ft) <= maxw: actual = prueba
    else: lineas.append(actual); actual = p
lineas.append(actual)
lineas = lineas[:2]
y = ay - 4 * S
for l in lineas:
    d.text((tx, y), l, font=ft, fill="white"); y += 44 * S
d.text((tx, y + 2 * S), CANAL, font=fc, fill=(235, 235, 235))

# Pie: logo YouTube + duración
by = ay + av + 64 * S
lx = cx + pad
lh, lw = 46 * S, 66 * S
d.rounded_rectangle([lx, by, lx + lw, by + lh], radius=13 * S, fill=(255, 0, 0))
tcx, tcy = lx + lw // 2 + 3 * S, by + lh // 2
d.polygon([(tcx - 10 * S, tcy - 12 * S), (tcx - 10 * S, tcy + 12 * S), (tcx + 13 * S, tcy)], fill="white")
fy = font("Inter-Bold.otf", 34)
d.text((lx + lw + 10 * S, by + lh // 2), "YouTube", font=fy, fill="white", anchor="lm")

fd = font("Inter-SemiBold.otf", 30)
dw = d.textlength(DURACION, font=fd)
rx = cx + cw - pad - dw
d.text((rx, by + lh // 2), DURACION, font=fd, fill="white", anchor="lm")
# ícono de "video" (rectángulo con play) antes del texto
ix = rx - 50 * S
d.rounded_rectangle([ix, by + 8 * S, ix + 38 * S, by + lh - 8 * S], radius=5 * S, outline="white", width=3 * S)
icx, icy = ix + 19 * S, by + lh // 2
d.polygon([(icx - 6 * S, icy - 8 * S), (icx - 6 * S, icy + 8 * S), (icx + 8 * S, icy)], fill="white")

img.resize((1080, 1920), Image.LANCZOS).save(SALIDA)
print("OK", SALIDA, fondo, tarjeta)
