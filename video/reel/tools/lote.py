#!/usr/bin/env python3
"""Procesa una carpeta de cuadros RGBA con sujeto.py (mismos parámetros para todos). Uso: lote.py entrada/ salida/ [args de sujeto.py]"""
import sys, glob, os
sys.argv = [sys.argv[0], 'x', 'y'] + sys.argv[3:] if False else sys.argv
src, dst = sys.argv[1], sys.argv[2]
sys.argv = ['sujeto.py', '', ''] + sys.argv[3:]
sys.path.insert(0, os.path.dirname(__file__))
import sujeto
from PIL import Image
os.makedirs(dst, exist_ok=True)
fs = sorted(glob.glob(src + '/*.png'))
for f in fs:
    sujeto.procesar(Image.open(f).convert('RGBA')).save(os.path.join(dst, os.path.basename(f)), compress_level=1)
print(len(fs), 'cuadros')
