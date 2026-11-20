#!/usr/bin/env python3
"""Prepara la capa del sujeto para el reel: RGBA (recorte) -> escala, color, luz de borde, enfoque, fundido.
Uso: python3 sujeto.py entrada_rgba.png salida.png [--scale 1.6] [--fade 0|1] [--extend PX] [--rim 0..1]
  --fade 0     sin fundido inferior (cuando el cuerpo lo corta un marco o el borde del cuadro)
  --extend PX  prolonga el torso (remera negra) PX píxeles hacia abajo"""
import sys, numpy as np
from PIL import Image, ImageFilter

arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
SCALE = arg('--scale', 1.6); FADE = arg('--fade', 1); EXTEND = arg('--extend', 0); RIM = arg('--rim', 0.0)
BLUE2 = np.array([0x00, 0x57, 0xFF], np.float32) / 255

def procesar(img):
    w, h = img.size
    W, H = round(w * SCALE), round(h * SCALE)
    img = img.resize((W, H), Image.LANCZOS)
    rgb = img.convert('RGB').filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    x = np.asarray(rgb, np.float32) / 255
    a = np.asarray(img.getchannel('A'), np.float32) / 255

    # --- color: menos blanco, más contraste, más frío (que parezca iluminado por el fondo)
    x = x ** 1.18                                   # baja medios y altas
    x = x * 0.9
    lum = (x @ np.array([.299, .587, .114], np.float32))[..., None]
    x = lum + (x - lum) * 0.82                      # menos saturación
    x = x * np.array([0.9, 0.96, 1.08], np.float32) # tinte azul
    x = (x - 0.5) * 1.08 + 0.5                      # contraste
    # luz azul de relleno desde los costados (como el fondo encendido)
    xs = np.linspace(-1, 1, W, dtype=np.float32)[None, :, None]
    side = np.clip(np.abs(xs) - 0.35, 0, 1) / 0.65
    x = x + side * BLUE2 * 0.10 * lum * 2

    # --- luz de borde (rim): banda interna del contorno
    am = Image.fromarray((a * 255).astype(np.uint8))
    er = np.asarray(am.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    rim = np.clip(a - er, 0, 1)[..., None]
    x = 1 - (1 - x) * (1 - rim * BLUE2 * 0.9 * RIM)  # screen azul en el borde (apagado por defecto)
    x = x + rim * 0.06 * RIM

    # --- fundido: torso hacia abajo y costados (remera negra -> fondo oscuro)
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    fy = np.clip((0.97 - ys) / 0.20, 0, 1)          # se va del 77% al 97% del alto
    fx = np.clip((1 - np.abs(xs[..., 0])) / 0.16, 0, 1)
    fx = fx * np.clip((ys - 0.72) / 0.1, 0, 1) + (1 - np.clip((ys - 0.72) / 0.1, 0, 1))  # costados solo en el torso
    fade = fy * np.maximum(fx, 0)
    fade = fade * fade * (3 - 2 * fade)
    if FADE: a = a * fade
    if EXTEND:
        x = np.concatenate([x, np.repeat(x[-1:], EXTEND, 0) * np.linspace(1, .6, EXTEND, dtype=np.float32)[:, None, None]], 0)
        a = np.concatenate([a, np.repeat(a[-1:], EXTEND, 0)], 0)

    out = np.dstack([np.clip(x, 0, 1) * 255, a * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

if __name__ == '__main__':
    procesar(Image.open(sys.argv[1]).convert('RGBA')).save(sys.argv[2])
