#!/usr/bin/env python3
"""Prepara la capa del sujeto para el reel: RGBA (recorte) -> escala, color, luz de borde, enfoque, fundido.
Uso: python3 sujeto.py entrada_rgba.png salida.png [--scale 1.6]"""
import sys, numpy as np
from PIL import Image, ImageFilter

SCALE = float(sys.argv[sys.argv.index('--scale') + 1]) if '--scale' in sys.argv else 1.6
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
    x = 1 - (1 - x) * (1 - rim * BLUE2 * 0.9)       # screen azul en el borde
    x = x + rim * 0.06

    # --- fundido: torso hacia abajo y costados (remera negra -> fondo oscuro)
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    fy = np.clip((0.97 - ys) / 0.20, 0, 1)          # se va del 77% al 97% del alto
    fx = np.clip((1 - np.abs(xs[..., 0])) / 0.16, 0, 1)
    fx = fx * np.clip((ys - 0.72) / 0.1, 0, 1) + (1 - np.clip((ys - 0.72) / 0.1, 0, 1))  # costados solo en el torso
    fade = fy * np.maximum(fx, 0)
    fade = fade * fade * (3 - 2 * fade)
    a = a * fade

    out = np.dstack([np.clip(x, 0, 1) * 255, a * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

if __name__ == '__main__':
    procesar(Image.open(sys.argv[1]).convert('RGBA')).save(sys.argv[2])
