# _fuente — el motor de la web

Aquí está todo lo necesario para **regenerar la web**. Esta carpeta no se publica (está en `.assetsignore`).

Las páginas `index.html` del proyecto **se generan** a partir de estos archivos. Si se edita un `index.html` a mano, el cambio se perderá la próxima vez que se regenere. Los cambios se hacen aquí y después se ejecuta:

```bash
py _fuente/construir.py
```

Hace falta Python 3 con Pillow (`py -m pip install pillow`). Para procesar vídeos, también ffmpeg.

## Qué hay aquí

| Archivo | Para qué |
|---|---|
| `construir.py` | Genera todas las páginas: plantilla, menú, pie, portada, productos, contacto… |
| `iconos.py` | Los iconos SVG de la web. Para añadir uno, se añade una línea al diccionario `ICONS`. |
| `contenido/productos.json` | Categorías y familias de producto, con su icono. **Añadir una familia = añadir una línea.** |
| `contenido/textos_productos.py` | Texto técnico (HTML) y tablas de cada familia. |
| `contenido/legal.json` | Textos legales. |
| `contenido/noticias-archivo.json` | Noticias antiguas de la web anterior (solo fecha y título). |
| `worker/index.js` | Programa de Cloudflare que recibe el formulario de presupuesto y lo envía por email. |
| `noticias.py`, `imagenes.py`, `compartir.py` | Noticias por carpetas, conversión de fotos a WebP e imágenes para compartir. |
| `publicar.bat` | Doble clic: regenera la web, comprueba enlaces y la sube. |
| `herramientas/procesar_fotos.py` | Convierte las fotos y vídeos de `web fotos/` al formato web. |
| `herramientas/comprobar.py` | Busca enlaces rotos e imágenes que no usa ninguna página. |

## Tareas habituales

**Añadir una familia de producto**
1. En `contenido/productos.json`, dentro de su categoría: `{"slug": "nueva-familia", "nombre": "Nueva familia", "icono": "parts"}`.
2. Opcional: su texto en `contenido/textos_productos.py` (`TEXT["categoria"]["nueva-familia"]`).
3. Opcional: fotos en `assets/img/productos/<categoria>/nueva-familia/01.webp, 02.webp…`
4. `py _fuente/construir.py` → aparece en la página, en el menú y en las tarjetas.

**Cambiar el teléfono, el email o el menú:** al principio de `construir.py`.

**Después de cualquier cambio:** `py _fuente/herramientas/comprobar.py` para revisar que no haya enlaces rotos.
