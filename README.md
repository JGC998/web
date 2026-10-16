# CRM Componentes — web

Web estática de **Comercial de Recambios Montemayor, S.L.** (CRM), hecha con HTML, CSS y JavaScript puros. No hay paso de compilación ni dependencias: Cloudflare la publica tal cual.

Diseño sencillo de tipo "página de producto": títulos grandes, un mensaje por bloque, iconos propios en lugar de fotos, y una barra fija de **Llamar / Email** en el móvil.

## Ramas

| Rama | Qué contiene |
|---|---|
| `produccion` | **La web actual.** Aquí se trabaja y desde aquí se publica. |
| `main` | Copia de la web original (WordPress) migrada a HTML. Se conserva como referencia; no se toca. |

Para probar cambios grandes sin tocar la web publicada, crea una rama a partir de `produccion` (por ejemplo `git checkout -b prueba-colores`). Cloudflare genera una vista previa de cada rama.

## Estructura

```
.
├── index.html                    # Inicio
├── productos/
│   ├── index.html                # Listado de productos
│   ├── elevacion/index.html
│   ├── bandas-transportadoras/index.html
│   ├── faldetas/index.html
│   └── bandas-pvc/index.html
├── catalogos/index.html
├── quienes-somos/index.html
├── noticias/index.html
├── contacto/index.html
├── legal/                        # Aviso legal, privacidad, cookies, redes sociales
├── 404.html                      # Página de error
├── assets/
│   ├── css/
│   │   ├── base.css              # Colores, tipografía y reset
│   │   ├── layout.css            # Barra superior, menú móvil, barra de producto, pie
│   │   └── components.css        # Iconos, botones, tarjetas, acordeones, tablas, contacto…
│   ├── js/
│   │   └── main.js               # Menú móvil, visor de fotos, mapa y acordeones
│   └── img/
│       ├── brand/                # Logo
│       ├── productos/<categoria>/<familia>/   # Fotos del carrusel de cada familia (01.webp, 02.webp…)
│       ├── empresa/              # Nave, maquinaria (Quiénes somos)
│       └── fondos/               # Foto de fondo de la portada
│   └── video/                    # Vídeos de fondo (MP4 720p sin sonido) + imagen fija (.jpg)
├── fotos-antiguas/               # Fotos de la web anterior, pendientes de retocar (NO se publican)
├── web fotos/                    # Originales del móvil (NO se suben a git ni se publican)
├── favicon.svg
├── _redirects                    # Redirecciones 301 de las URLs antiguas de WordPress
├── _headers                      # Cabeceras HTTP (seguridad y caché)
├── wrangler.jsonc                # Configuración del despliegue en Cloudflare
├── .assetsignore                 # Archivos del repo que no se publican
├── robots.txt
└── sitemap.xml
```

Cada página es una carpeta con su `index.html`, así las URLs quedan limpias (`/productos/faldetas/`).

## Ver la web en local

Las rutas son absolutas (`/assets/...`), así que hay que abrirla con un servidor y no con doble clic:

```bash
python -m http.server 8000
# y abrir http://localhost:8000
```

## Despliegue en Cloudflare

La web es un **Cloudflare Worker con contenido estático** (`web-crm`), conectado a este repositorio:

- Cada `git push` a **`produccion`** publica la web (`npx wrangler deploy`).
- Las demás ramas generan una **vista previa** (`npx wrangler preview`), sin tocar la web publicada.

Archivos de configuración:

- `wrangler.jsonc`: nombre del Worker, carpeta publicada, página 404 y el bloque `previews` (necesario para las vistas previas).
- `.assetsignore`: archivos que **no** se publican (`.git`, este README, la configuración…). Si añades al repo algo que no deba verse en la web, apúntalo aquí.
- `_redirects` y `_headers`: redirecciones y cabeceras; funcionan igual en Workers.

## Cómo editar

- **Textos:** directamente en el `index.html` de cada página.
- **Colores y tipografía:** variables al principio de `assets/css/base.css` (`--green`, `--text`, `--tile`…).
- **Menú y pie:** se repiten en cada página; si cambian, hay que cambiarlos en todos los `.html`.
- **Iconos:** son SVG escritos dentro del propio HTML, con trazo de 24×24 y la clase `icon`, que toman el color del texto:
  ```html
  <svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="7"/></svg>
  ```
  Para usar un icono que ya existe en otra página, copia su `<svg>…</svg>`. Dentro de un recuadro verde: `<span class="badge-icon">…</span>`.
- **Fotos de producto (carrusel):** cada familia muestra un carrusel con las fotos de su carpeta, por ejemplo `assets/img/productos/elevacion/cangilones/`. Las fotos se procesan antes (máx. 1400 px, WebP) y se nombran `01.webp`, `02.webp`… en el orden en que deben salir. Al añadirlas hay que regenerar la página de esa categoría para que el carrusel aparezca. Si una familia no tiene fotos, no se muestra carrusel.
- **Fotos y vídeos nuevos:** los originales del móvil se dejan en `web fotos/` (está en `.gitignore`: no se suben a GitHub ni se publican). Antes de usarlos se procesan: fotos a 1400 px en WebP y sin metadatos (se elimina la ubicación GPS) y vídeos a MP4 720p sin sonido. Los vídeos de fondo solo se descargan si el visitante no tiene activado el ahorro de datos ni la reducción de animaciones.
- **Fotos antiguas:** están en `fotos-antiguas/` (mismos nombres que tenían). No se usan ni se publican; sirven para retocarlas y volver a subirlas.
- **Caché de CSS y JS:** `_headers` hace que el navegador compruebe en cada visita si han cambiado, así que los cambios se ven al momento. Los enlaces llevan una versión (`base.css?v=20261015`); si algún día se vuelve a cachear durante más tiempo, hay que subir ese número en todas las páginas al cambiar el CSS o el JS.

## Pendiente / notas

- **Catálogos PDF:** la web antigua no tenía los PDF. Ahora cada catálogo se pide por email. Cuando estén los PDF, se ponen en `assets/docs/` y se cambia el enlace.
- **Formulario de contacto:** no hay (necesitaba WordPress). El contacto es por teléfono y email.
- **Mapa:** solo se carga al pulsar "Mostrar mapa", así Google no pone cookies sin permiso. La web no usa cookies propias.
- **Textos legales:** son los de la web antigua. Conviene revisarlos (ya no hay formulario y la política de cookies habla de cookies que ya no se usan).
- **Dominio:** `SITE` al principio de `_fuente/construir.py` (ahora `https://crmgestiontaller.com`). Se usa en `sitemap.xml`, `robots.txt` y las imágenes para compartir. Al migrar a `crmsl.es`, cambiarlo y regenerar.
- **Imágenes para compartir:** se generan solas en `assets/img/compartir/` (1200×630) con la foto, el logo y el título de cada página.
