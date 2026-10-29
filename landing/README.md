# Landing · Rumor 2026

Landing estática (HTML + CSS + JS, sin build). Abrir `landing/index.html` servida por HTTP
(ej. `npx serve landing`) o subir la carpeta tal cual a cualquier hosting.

## Estructura
1. **Hero** – fondo vivo en WebGL (la misma niebla + cinta de luz del video de servicios, en horizontal y sin textos) con mensajes flotantes de logros.
2. **Marcas** – marquee con clientes.
3. **Nosotros** – sección fija con scroll: aparecen 3 cards glass (+3 años, +60 clientes, 82%) y al final el cierre "Por eso, antes de ejecutar, diagnosticamos…".
4. **Reel** – marco que se expande al scrollear. Poner el video en `assets/reel.mp4` (16:9, 20–40 s, <8 MB). Sin video muestra un placeholder animado.
5. **Cómo trabajamos** – claim + texto y animación de pasos (Diagnóstico → … → Resultado).
6. **Packs** – 3 cards de pantalla completa que se apilan (Fundacional / Estrategia 360 / Acelerador).
7. **Servicios** – acordeón de 9 servicios.
8. **Casos** – Finteem con contadores.
9. **Testimonios** – cards de video; completar `data-video="assets/testimonios/x.mp4"` en cada `.t-card`.
10. **Hablemos** – bloque CTA con botón a WhatsApp (+54 9 3541 54-9822).

## Editar
- Mensajes del hero: `HERO_MESSAGES` en `script.js`.
- Colores: variables en `:root` de `styles.css`.
- Tipografías: Unbounded (títulos) + Inter Tight (texto), desde Google Fonts.
