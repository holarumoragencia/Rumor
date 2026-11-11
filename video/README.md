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

`video/rumor-talking/index.html`: reel vertical 1080×1920 de 12 s en loop, con estética de pantalla retro (CRT).

- 3 momentos de 4 s: inglés → español → spanglish. En cada uno: deformado → **calma (~1,6 s, se lee)** → deformado.
  El idioma cambia en el pico de la deformación.
- La frase va partida en dos renglones que se alternan ("Everyone's talking." / "Are they talking about you?").
- "you" / "vos" en crimson pink `#fd6e88` con halo difuso que tiñe las letras vecinas.
- Ondas amplias y orgánicas, leve inclinación y renglones que se deslizan distinto (nada queda perfecto).
- Glitch retro (~0,7 s) en cada cambio de idioma: franjas desplazadas, aberración fuerte y cambio en bloques.
- Post-proceso retro: resplandor de fósforo, aberración cromática, líneas de barrido, temblor y franja de tracking, parpadeo y grano.
- **Fondo negro** (`?bg=black`): `#191919`, letras azul `#0057ff` + capa difusa de crema azulado.
- **Fondo crema** (`?bg=cream`): `#fffcf1`, letras azul `#003afe` + capa difusa negra.

Exportar:

```bash
node video/render.cjs --page rumor-talking/index.html --out out/rumor-talking-negro.mp4
node video/render.cjs --page rumor-talking/index.html --query bg=cream --out out/rumor-talking-crema.mp4
```

Textos en `LANGS`, duración por idioma en `SEG`, curva de calma en `render(t)` (`calm`/`amp`), colores en `PAL` / `THEME`.
