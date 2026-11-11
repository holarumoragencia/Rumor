# Video vertical · Servicios Rumor

Pieza 1080×1920 (9:16) con fondo difuminado en movimiento (shader WebGL) en la paleta Rumor
—azul `#003afe` / `#0057ff`, negro `#191919`, crema `#fffcf1`— más una cinta de luz que se dibuja y gira,
grano y texto con entrada por desenfoque. Inspirado en la estética de flyers de eventos, con la identidad Rumor 2026.

Guion (15 s):
- 0–2 s: aparece el fondo, se dibuja la cinta, entra el logo `rumor agencia` + "Not just / an agency".
- 2–5 s: entran los servicios: Paid Media · Web · Diseño & Social Media · Consultoría de negocio · Estrategia de marca.
- 5–9.6 s: "From noise / to structure" + botón "Hablemos".
- 10–15 s: cierre con el isotipo R, "No vendemos servicios sueltos. Vendemos un sistema." y logo.

## Uso

- **Vista previa:** abrir `video/index.html` en Chrome (corre en loop).
- **Exportar MP4:** `node video/render.cjs` → `video/out/rumor-servicios.mp4` (requiere Playwright + ffmpeg).
- **Un cuadro suelto:** `node video/render.cjs --still 7` → PNG del segundo 7.

## Editar

Todo está en `video/index.html`:
- Textos: bloque HTML `#services`, `.tag`, `.foot`, `#endLine`.
- Tiempos: función `render(t)` (cada `env(t, entrada, duración, salida)`); duración total en `DURATION`.
- Colores del difuminado: shader `FS` (`mist`, `black`, `blue`, `blue2`, `deep`).

Tipografías: Arial (sistema) para textos; "agencia" usa Graphie si está instalada (cae a Inter ExtraLight).

---

# Reel · "Everyone's talking. Are they talking about you?"

`video/rumor-talking/index.html`: reel vertical 1080×1920 de 10 s en loop. La frase se repite en mosaico
(inglés, español y spanglish, una fila por idioma) y se deforma con remolinos líquidos. En algunos momentos
la frase se lee grande y en otros se vuelve textura. "you" y "vos" van en crimson pink `#fd6e88`, con un halo difuso que tiñe las letras vecinas.

- **Fondo negro** (`?bg=black`): fondo `#191919`, letras azul Rumor `#0057ff` que se funden con un crema que vira a azul claro.
- **Fondo crema** (`?bg=cream`): fondo `#fffcf1`, letras azul `#003afe` que se funden con negro `#191919`.

Exportar:

```bash
node video/render.cjs --page rumor-talking/index.html --out out/rumor-talking-negro.mp4
node video/render.cjs --page rumor-talking/index.html --query bg=cream --out out/rumor-talking-crema.mp4
```

Textos en el array `PHRASES` (el segundo tramo de cada frase es el acento). Colores en `PAL` / `THEME`.
