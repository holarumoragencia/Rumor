#!/usr/bin/env python3
"""Sintetiza los efectos de sonido (sin samples de terceros) y arma la pista según cues.json.

Uso: python3 sfx.py cues.json salida.wav DURACION
cues.json = [[t_segundos, "nombre", ganancia], ...]  (lo exporta index.html → window.SFX)
"""
import json
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)


def env(n, a, d):
    """ataque lineal a muestras, caída exponencial con constante d (s)."""
    t = np.arange(n) / SR
    e = np.exp(-np.maximum(t - a, 0) / d)
    e[: int(a * SR)] = np.linspace(0, 1, int(a * SR), endpoint=False) if a > 0 else e[:0]
    return e


def tone(freqs, dur, shape=np.sin):
    f = np.interp(np.arange(int(dur * SR)), np.linspace(0, int(dur * SR), len(freqs)), freqs)
    return shape(2 * np.pi * np.cumsum(f) / SR)


def whoosh(dur=0.5, lo=300, hi=2600):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    # barrido de banda en bloques
    blocks = 24
    for i in range(blocks):
        a, b = i * n // blocks, (i + 1) * n // blocks
        u = i / (blocks - 1)
        fc = lo + (hi - lo) * np.sin(np.pi * u) ** 1.5
        sos = butter(2, [fc * 0.6, min(fc * 1.6, SR / 2 - 100)], 'bandpass', fs=SR, output='sos')
        out[a:b] = sosfilt(sos, noise[max(a - 2000, 0):b])[-(b - a):]
    t = np.linspace(0, 1, n)
    e = np.sin(np.pi * t ** 0.7) ** 2
    return out * e / np.abs(out).max()


def pop_in():  # mensaje recibido: dos notas cortas, burbujeantes
    a = tone([620, 930], 0.09) * env(int(0.09 * SR), 0.004, 0.035)
    b = tone([930, 1240], 0.16) * env(int(0.16 * SR), 0.004, 0.06)
    out = np.zeros(int(0.25 * SR))
    out[: len(a)] += a
    out[int(0.075 * SR): int(0.075 * SR) + len(b)] += b * 0.9
    return out


def pop_typing():  # aparece "escribiendo": blip suave grave
    return tone([480, 560], 0.12) * env(int(0.12 * SR), 0.003, 0.04) * 0.8


def click():
    n = int(0.05 * SR)
    nz = sosfilt(butter(2, 2500, 'highpass', fs=SR, output='sos'), rng.standard_normal(n))
    return (nz * env(n, 0.0005, 0.004) * 0.7 + tone([3200], 0.05) * env(n, 0.0005, 0.008) * 0.5)


def impact():  # entrada de la R
    n = int(0.6 * SR)
    sub = tone([140, 48], 0.6) * env(n, 0.002, 0.16)
    nz = sosfilt(butter(2, 900, 'lowpass', fs=SR, output='sos'), rng.standard_normal(n)) * env(n, 0.001, 0.03)
    return sub * 0.9 + nz * 0.5


def shimmer():
    n = int(0.9 * SR)
    out = np.zeros(n)
    for i, f in enumerate([2093, 2637, 3136, 4186]):
        s = int(i * 0.06 * SR)
        k = tone([f], 0.9 - i * 0.06) * env(n - s, 0.002, 0.18)
        out[s:] += k * 0.25
    return out


def tick():  # tecla suave
    n = int(0.03 * SR)
    return sosfilt(butter(2, [1500, 5000], 'bandpass', fs=SR, output='sos'), rng.standard_normal(n)) * env(n, 0.0005, 0.006)


SOUNDS = {
    'whoosh': lambda: whoosh(0.45),
    'whoosh_long': lambda: whoosh(0.7, 200, 1800),
    'swish': lambda: whoosh(0.28, 900, 5000) * 0.7,
    'pop_in': pop_in,
    'pop_typing': pop_typing,
    'click': click,
    'impact': impact,
    'shimmer': shimmer,
    'tick': tick,
}


def main():
    cues, out_path, dur = json.load(open(sys.argv[1])), sys.argv[2], float(sys.argv[3])
    mix = np.zeros((int(dur * SR) + SR, 2))
    for t, name, gain, *pan in cues:
        s = SOUNDS[name]() * gain
        p = pan[0] if pan else 0.0
        i = int(t * SR)
        seg = mix[i:i + len(s)]
        seg[:, 0] += s[: len(seg)] * np.sqrt((1 - p) / 2) * 1.414
        seg[:, 1] += s[: len(seg)] * np.sqrt((1 + p) / 2) * 1.414
    mix = mix[: int(dur * SR)]
    # fade de salida y limitador suave
    f = int(0.4 * SR)
    mix[-f:] *= np.linspace(1, 0, f)[:, None]
    mix = np.tanh(mix * 1.1) * 0.89
    pcm = (mix * 32767).astype('<i2')
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    main()
