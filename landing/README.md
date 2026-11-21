# Landing · Rumor 2026

Landing estática (HTML + CSS + JS, sin build). Abrir `landing/index.html` servida por HTTP
(ej. `npx serve landing`) o subir la carpeta tal cual a cualquier hosting.

## Estructura
1. **Hero** – modo claro: fondo vivo en WebGL (niebla azul sobre crema + cinta de luz) con mensajes flotantes de logros en liquid glass.
2. **Marcas** – "Trabajamos con" + marquee de clientes.
3. **Nosotros** – foto de fondo (`assets/nosotros.webp`); al scrollear aparecen juntas las 3 cards en liquid glass (+3 años, +60 clientes, 82%).
4. **Reel** – marco que se expande al scrollear, con el claim "Lo que hacemos, en movimiento." encima. Poner el video en `assets/reel.mp4` (16:9, 20–40 s, <8 MB). Sin video muestra un placeholder animado.
5. **Cómo trabajamos** – claim + texto y animación de pasos (Diagnóstico → … → Resultado).
6. **Packs** – 3 cards en liquid glass que se apilan sobre un fondo gaussiano claro (Fundacional / Estrategia 360 / Acelerador, con la curva de lanzamiento animada).
7. **Servicios** – acordeón de 9 servicios; a la izquierda el botón "Agendá un diagnóstico gratuito".
8. **Casos** – Finteem con contadores.
9. **Testimonios** – cards de video; completar `data-video="assets/testimonios/x.mp4"` en cada `.t-card`.
10. **Hablemos** – bloque CTA con botón a WhatsApp (+54 9 3541 54-9822).

## Editar
- Mensajes del hero: `HERO_MESSAGES` en `script.js`.
- Colores: variables en `:root` de `styles.css`.
- Tipografías: **Myriad Pro** para títulos y claims (Black; acentos en SemiExtended Light Italic; números y servicios en SemiExtended) y **Arial** para párrafos.
  - Para que la vean todos los visitantes: en fonts.adobe.com crear un *Web Project* con Myriad Pro (Light, Regular, Semibold, Bold, Black y sus SemiExtended) y pegar el `<link>` del kit en `index.html` donde indica el comentario. Agregar el dominio al proyecto.
  - Alternativa: subir los `.woff2` (con licencia web) a `assets/fonts/` con los nombres de `fonts.css` (ej. `MyriadPro-Black.woff2`).
  - Si Myriad Pro está instalada en la compu, el navegador ya la usa localmente.

## SEO y seguridad (ya incluido)
- `index.html`: título y descripción para Google, URL canónica, vista previa al compartir (Open Graph / X con `og-image.jpg`), favicon y datos estructurados (schema.org) con teléfono, mail y redes.
- `robots.txt` y `sitemap.xml`: para que Google rastree el sitio. Dar de alta el sitemap en Google Search Console.
- `.htaccess`: fuerza HTTPS y dominio sin `www`, cabeceras de seguridad, compresión y caché. Incluye una CSP comentada para activar cuando estén definidos los scripts externos (Pixel, GA…).
- `404.html`: página de error con la marca.
- **Dominio:** todo apunta a `https://rumoragencia.com/`. Si el dominio es otro, reemplazarlo en `index.html`, `robots.txt` y `sitemap.xml`.

## Liquid glass
Clase `.lg` en `styles.css`: desenfoque + tinte + brillos de borde. En Chrome/Edge se suma la deformación del fondo
(filtros SVG `#lg-distort` y `#lg-distort-soft` al comienzo de `index.html`). Cada elemento ajusta `--lg-tint`, `--lg-blur` y `--lg-filter`.
