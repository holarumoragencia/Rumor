#!/usr/bin/env python3
"""Genera reel/subs.js: subtítulos de a una palabra con sus tiempos.
Cada tramo = una frase detectada en el audio (inicio, fin, texto). Dentro del tramo,
el tiempo se reparte según las sílabas de cada palabra. Las palabras de 1-2 letras
se pegan a la siguiente para que no parpadeen."""
import re, json, os

# Tiempos en segundos dentro de cada archivo de audio (detección de silencios, -32 dB)
TRAMOS = {
  'p1': [  # primera_parte.mp4
    (0.42, 2.77, 'Solo 7 días para el comienzo de Black Friday'),
    (3.35, 5.08, 'Y en Rumor preparamos un checklist'),
    (5.40, 6.01, 'especial'),
    (6.43, 7.30, 'para que puedas saber'),
    (7.63, 9.45, 'si ya estás listo para comenzar la campaña'),
    (9.60, 10.10, 'Vení que te muestro'),
  ],
  'vo': [  # voz_de_fondo_del_medio.wav (se usa hasta 21,75 s; lo que sigue se repite en el final)
    (1.14, 2.18, 'Son 15 puntos'),
    (2.39, 3.31, 'en 5 etapas'),
    (3.49, 5.01, 'que las vas a hacer en menos de 2 minutos'),
    (5.58, 6.23, 'El destino'),
    (6.76, 7.59, 'La medición'),
    (8.11, 8.81, 'La oferta'),
    (9.34, 10.19, 'La respuesta'),
    (10.85, 11.66, 'Y el presupuesto'),
    (12.51, 13.77, 'Marcás lo que ya resolviste'),
    (14.28, 15.27, 'Lo que queda en blanco'),
    (15.65, 16.32, 'es tu tarea'),
    (16.77, 17.93, 'pendiente para esta semana'),
    (18.66, 20.66, 'Y al final te dice si estás listo'),
    (21.03, 21.57, 'o todavía no'),
  ],
  'fin': [  # final.mp4
    (0.70, 3.40, 'Si querés usar esta herramienta gratuita comentá Black'),
    (3.78, 4.83, 'y te lo enviamos por privado'),
  ],
}
LEER = {'15': 'quince', '7': 'siete', '5': 'cinco', '2': 'dos'}

def silabas(w):
    w = LEER.get(w, w).lower().replace('\u00a0', ' ')
    return max(1, len(re.findall(r'[aeiouáéíóúü]+', w)))

def tramo_a_palabras(t0, t1, texto):
    ws = texto.replace('Black Friday', 'Black\u00a0Friday').split(' ')
    PROPIOS = {'Rumor', 'Black', 'Black\u00a0Friday'}
    ws = [w if w in PROPIOS else w.lower() for w in ws]
    pesos = [silabas(w) + 0.35 for w in ws]
    tot, acc, out = sum(pesos), t0, []
    for w, p in zip(ws, pesos):
        d = (t1 - t0) * p / tot
        out.append([round(acc, 3), round(acc + d, 3), w]); acc += d
    # pegar palabras cortas a la siguiente
    res = []
    for s, e, w in out:
        if res and len(res[-1][2].split()[-1]) <= 2 and len(res[-1][2].split()) < 3:
            res[-1][1] = e; res[-1][2] += ' ' + w
        else:
            res.append([s, e, w])
    if len(res) > 1 and len(res[-1][2]) <= 2:  # corta al final: va con la anterior
        res[-2][1] = res[-1][1]; res[-2][2] += ' ' + res[-1][2]; res.pop()
    return res

subs = {k: [p for tr in v for p in tramo_a_palabras(*tr)] for k, v in TRAMOS.items()}
dst = os.path.join(os.path.dirname(__file__), '..', 'subs.js')
open(dst, 'w').write('// Generado por tools/subs.py: [inicio, fin, texto] en segundos de cada audio\nwindow.SUBS = ' + json.dumps(subs, ensure_ascii=False, indent=0) + ';\n')
for k, v in subs.items(): print(k, ' | '.join(x[2] for x in v))
