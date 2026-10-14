# CRM Componentes — web

Web estática de **Comercial de Recambios Montemayor, S.L.** (CRM), reconstruida desde la antigua web en WordPress ([crmsl.es](https://crmsl.es)) con HTML, CSS y JavaScript puros. No hay paso de compilación ni dependencias, así que Cloudflare Pages la sirve tal cual.

## Estructura

```
.
├── index.html                    # Inicio
├── quienes-somos/index.html
├── productos/
│   ├── index.html                # Listado de productos
│   ├── elevacion/index.html
│   ├── bandas-transportadoras/index.html
│   ├── faldetas/index.html
│   └── bandas-pvc/index.html
├── catalogos/index.html
├── noticias/index.html
├── contacto/index.html
├── legal/
│   ├── aviso-legal/index.html
│   ├── politica-de-privacidad/index.html
│   ├── politica-de-cookies/index.html
│   └── politica-de-redes-sociales/index.html
├── 404.html                      # Página de error (Cloudflare la usa automáticamente)
├── assets/
│   ├── css/
│   │   ├── base.css              # Variables (colores, fuentes), reset, tipografía
│   │   ├── layout.css            # Cabecera, menú, banners de página, pie
│   │   └── components.css        # Botones, tarjetas, galerías, tablas, contacto…
│   ├── js/
│   │   └── main.js               # Menú móvil, desplegable, galería ampliable, mapa
│   └── img/
│       ├── brand/                # Logo
│       ├── inicio/  quienes-somos/  catalogos/  contacto/
│       ├── productos/<categoria>/          # Fotos grandes (máx. 1600 px)
│       │   └── thumbs/                     # Miniaturas 480×360 para las galerías
│       └── noticias/ (+ thumbs/)
├── favicon.svg
├── _redirects                    # Redirecciones 301 de las URLs antiguas de WordPress
├── _headers                      # Cabeceras HTTP (seguridad y caché)
├── wrangler.jsonc                # Configuración del despliegue en Cloudflare
├── .assetsignore                 # Archivos que no se publican
├── robots.txt
└── sitemap.xml
```

Cada página es una carpeta con su `index.html`, así las URLs quedan limpias (`/productos/faldetas/`).

## Ver la web en local

Las rutas son absolutas (`/assets/...`), así que hay que abrirla con un servidor y no con doble clic sobre el archivo:

```bash
python -m http.server 8000
# y abrir http://localhost:8000
```

## Despliegue en Cloudflare

La web se despliega como **Cloudflare Worker con contenido estático**, conectado a este repositorio. Cada `git push` a `main` vuelve a publicarla: Cloudflare ejecuta `npx wrangler deploy`, que lee `wrangler.jsonc`.

- `wrangler.jsonc`: nombre del Worker, carpeta publicada (`.`) y uso de `404.html` para las páginas que no existen.
- `.assetsignore`: archivos del repo que **no** se publican (`.git`, este README, la configuración…). Si se añade al repo algún archivo que no deba verse en la web, hay que añadirlo aquí.
- `_redirects` y `_headers` también funcionan en Workers.

Para usar el dominio propio: en el Worker, **Settings → Domains & Routes → Add → Custom domain**.

## Cómo editar contenido

- **Textos:** se editan directamente en el `index.html` de cada página.
- **Añadir una foto a una galería:** se guarda la imagen grande en `assets/img/productos/<categoria>/`, una miniatura de 480×360 con el mismo nombre en `.../thumbs/`, y se añade un enlace dentro del `<div class="gallery">` correspondiente:
  ```html
  <a href="/assets/img/productos/faldetas/goma-17.jpg" data-gallery="goma">
    <img src="/assets/img/productos/faldetas/thumbs/goma-17.jpg" alt="Goma — imagen 17" width="480" height="360" loading="lazy">
  </a>
  ```
  Los enlaces que comparten el mismo `data-gallery` forman una galería navegable.
- **Colores y fuentes:** variables en `assets/css/base.css` (`--green`, `--ink`, etc.).
- **Menú y pie:** se repiten en cada página. Si se cambian, hay que cambiarlos en todos los `.html`.
- **Caché de CSS y JS:** `_headers` hace que el navegador compruebe en cada visita si los CSS/JS han cambiado, así que los cambios se ven al momento. Los enlaces llevan una versión (`base.css?v=20261014`); si algún día se vuelve a cachear de forma larga, hay que subir ese número en todas las páginas al cambiar el CSS o el JS.

## Pendiente / notas

- **Catálogos PDF:** en la web antigua los botones "Descargar PDF" no llevaban a ningún archivo. Ahora son un botón "Solicitar catálogo" que abre un email. Cuando estén los PDF, se ponen en `assets/docs/` y se cambia el enlace.
- **Formulario de contacto:** se ha quitado, porque necesitaba WordPress. El contacto es por teléfono y email.
- **Mapa:** solo se carga cuando el usuario pulsa "Mostrar mapa", así Google no pone cookies sin permiso. La web no usa cookies propias.
- **Textos legales:** son los mismos que en la web antigua. Conviene revisarlos (por ejemplo, ya no hay formulario y la política de cookies habla de cookies que ya no se usan).
- `sitemap.xml` y `robots.txt` apuntan a `https://crmsl.es`. Si el dominio final es otro, hay que cambiarlo.
