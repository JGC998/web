"""Lee las noticias de _fuente/contenido/noticias/ (una carpeta por noticia).

Cada carpeta contiene:
  noticia.txt   cabecera "clave: valor" (titulo, fecha, resumen, borrador),
                una línea en blanco y después el texto de la noticia
  fotos         .jpg / .png en el orden de su nombre; la llamada "portada.*" va primero

Las fotos se convierten a WebP en assets/img/noticias/<slug>/ (01.webp, 02.webp…).
Los originales no se suben a GitHub (.gitignore); si no están, se usan las ya convertidas.
Las carpetas que empiezan por "_" (como _plantilla) se ignoran.
"""
import os, re, html, unicodedata, shutil

from imagenes import es_foto, procesar

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def slugify(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def fecha_larga(iso):
    a, m, d = iso.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {a}"


def leer_txt(ruta):
    """Separa la cabecera (clave: valor) del cuerpo."""
    meta, cuerpo, en_cabecera = {}, [], True
    for linea in open(ruta, encoding="utf-8-sig").read().splitlines():
        if en_cabecera:
            if not linea.strip():
                en_cabecera = False
                continue
            m = re.match(r"\s*([a-zA-ZáéíóúñÁÉÍÓÚÑ]+)\s*:\s*(.*)", linea)
            if m:
                meta[slugify(m.group(1))] = m.group(2).strip()
                continue
            en_cabecera = False
        cuerpo.append(linea)
    return meta, "\n".join(cuerpo).strip()


def texto_a_html(texto):
    """Párrafos separados por línea en blanco, listas con '- ' y **negritas**."""
    bloques = []
    for bloque in re.split(r"\n\s*\n", texto.strip()):
        lineas = [l.strip() for l in bloque.splitlines() if l.strip()]
        if not lineas:
            continue
        fmt = lambda l: re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(l))
        if all(l.startswith("- ") for l in lineas):
            bloques.append("<ul>" + "".join(f"<li>{fmt(l[2:])}</li>" for l in lineas) + "</ul>")
        else:
            bloques.append("<p>" + "<br>".join(fmt(l) for l in lineas) + "</p>")
    return "\n".join(bloques)


def _fotos(carpeta, slug, repo):
    """Convierte las fotos originales (si están) y devuelve las rutas web."""
    originales = sorted((f for f in os.listdir(carpeta) if es_foto(f)),
                        key=lambda f: (not f.lower().startswith("portada"), f.lower()))
    destino = os.path.join(repo, "assets", "img", "noticias", slug)
    if originales:
        hechas = sorted(os.listdir(destino)) if os.path.isdir(destino) else []
        ultima = max(os.path.getmtime(os.path.join(carpeta, f)) for f in originales)
        al_dia = len(hechas) == len(originales) and all(
            os.path.getmtime(os.path.join(destino, f)) >= ultima for f in hechas)
        if not al_dia:
            shutil.rmtree(destino, ignore_errors=True)
            for i, f in enumerate(originales, 1):
                procesar(os.path.join(carpeta, f), os.path.join(destino, f"{i:02d}.webp"))
            print(f"  noticia '{slug}': {len(originales)} fotos convertidas")
    if not os.path.isdir(destino):
        return []
    return [f"assets/img/noticias/{slug}/{f}" for f in sorted(os.listdir(destino)) if f.endswith(".webp")]


def leer_noticias(fuente, repo):
    base = os.path.join(fuente, "contenido", "noticias")
    noticias = []
    for nombre in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        carpeta = os.path.join(base, nombre)
        txt = os.path.join(carpeta, "noticia.txt")
        if nombre.startswith(("_", ".")) or not os.path.isfile(txt):
            continue
        meta, cuerpo = leer_txt(txt)
        if meta.get("borrador", "no").lower() in ("si", "sí", "yes", "true"):
            continue
        if "titulo" not in meta:
            raise SystemExit(f"Falta 'titulo:' en {txt}")
        fecha = meta.get("fecha") or (re.match(r"\d{4}-\d{2}-\d{2}", nombre) or [None])[0]
        if not fecha or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha):
            raise SystemExit(f"Falta 'fecha: AAAA-MM-DD' en {txt}")
        slug = slugify(meta.get("slug") or meta["titulo"])
        noticias.append({
            "slug": slug,
            "titulo": meta["titulo"],
            "fecha": fecha,
            "fecha_larga": fecha_larga(fecha),
            "resumen": meta.get("resumen", ""),
            "html": texto_a_html(cuerpo),
            "fotos": _fotos(carpeta, slug, repo),
        })
    return sorted(noticias, key=lambda n: n["fecha"], reverse=True)
