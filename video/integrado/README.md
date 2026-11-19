# Reel · "Todo integrado, todos los meses." (Gemini Travel)

Animación 1080×1920, 10 s, 30 fps, con efectos de sonido sintetizados (sin audio de terceros).

Guion:
- 0.25–1.4 s: entran las cards Contenido / Anuncios / Medición con desenfoque de movimiento y rebote.
- 0.95–2.4 s: el cursor entra en curva y hace click en "Anuncios" (onda + brillo + sonido).
- 2.2–4 s: título palabra por palabra (sube desde la línea base con desenfoque) y bajada línea por línea.
- 4.1 s: la R de Rumor entra girando con destello e impacto.
- 4.75 / 5.45 / 6.15 s: burbujas del chat con sonido de mensaje y "escribiendo…" animado.
- 6.75–7.9 s: Aruba sube desde abajo, Samaná y Natal se abren desde detrás; 8.1 s brillo sobre las promos.

## Uso
- Vista previa: abrir `video/integrado/index.html` en Chrome.
- Exportar: `node video/integrado/render.cjs` → `video/integrado/out/todo-integrado.mp4`.
- Cuadro suelto: `node video/integrado/render.cjs --still 7`.
- Capas: `python3 video/integrado/extract.py` (usa `src/`; lo que no vino suelto se recorta de `src/referencia.webp`).
- Tiempos y sonidos: objeto `T` y `window.SFX` en `index.html`; los sonidos están en `sfx.py`.
