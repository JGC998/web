"""Procesa las fotos y vídeos originales de 'web fotos/' para la web.

- Fotos: enderezadas (EXIF), reducidas al tamaño web y guardadas en WebP SIN metadatos
  (se elimina la ubicación GPS del móvil).
- Fotos de la web anterior ('web fotos/web anterior/'): solo las de buena resolución, con un
  retoque suave de contraste, color y nitidez.
- Vídeos: H.264 720p sin sonido, optimizados para empezar a reproducirse enseguida,
  más una imagen fija (poster).

Uso (desde la raíz del proyecto):  py _fuente/herramientas/procesar_fotos.py
La selección se define abajo por NOMBRE de archivo (PRODUCTOS, EMPRESA, SECTORES, FONDOS, VIDEOS),
así que añadir fotos nuevas a una carpeta no cambia las que ya se usan.
"""
import os, re, sys, subprocess, shutil, tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imagenes import procesar  # WebP sin metadatos
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

Image.MAX_IMAGE_PIXELS = None  # fotos de 200 MP del móvil

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "web fotos")
REF = os.path.join(REPO, "WEB NUEVA 2026")   # material del borrador de on3d (noviembre 2025)
TMP = tempfile.gettempdir()


def f(carpeta, *nombres):
    """Fotos de 'web fotos/<carpeta>/' por nombre de archivo."""
    return [os.path.join(SRC, carpeta, n) for n in nombres]


def ref(*ruta):
    """Foto de 'WEB NUEVA 2026/'."""
    return os.path.join(REF, *ruta)


def retocada(ruta):
    """Retoque suave de una foto de la web anterior: contraste, color y nitidez."""
    im = ImageOps.autocontrast(Image.open(ruta).convert("RGB"), cutoff=0.5)
    im = ImageEnhance.Color(im).enhance(1.06)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=3))
    destino = os.path.join(TMP, "crm-retocada-" + os.path.basename(ruta))
    im.save(destino, quality=95)
    return destino


def ant(*rutas):
    """Fotos de la web anterior ('web fotos/web anterior/'), retocadas."""
    return [retocada(os.path.join(SRC, "web anterior", r)) for r in rutas]


def recortada(ruta, caja):
    """Recorte de una foto; caja = (x0, y0, x1, y1) en fracciones del ancho y alto."""
    im = Image.open(ruta)
    im.draft("RGB", (4000, 4000))
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    im = im.crop((round(caja[0] * w), round(caja[1] * h), round(caja[2] * w), round(caja[3] * h)))
    destino = os.path.join(TMP, "crm-recorte-" + os.path.basename(ruta))
    im.save(destino, quality=95)
    return destino


def jpeg_de_pdf(pdf):
    """Extrae la foto incrustada en un PDF (la de faldetas viene dentro de un PDF). Se queda con el
    JPEG que más ocupa: el PDF lleva además un recuadro en blanco que es más grande pero casi vacío."""
    datos = open(pdf, "rb").read()
    fotos = [m for m in re.finditer(rb"<<(.{0,600}?)>>\s*stream\r?\n", datos, re.S) if b"DCTDecode" in m.group(1)]
    m = max(fotos, key=lambda m: datos.find(b"endstream", m.end()) - m.end())
    destino = os.path.join(TMP, "crm-" + os.path.basename(pdf) + ".jpg")
    open(destino, "wb").write(datos[m.end():datos.find(b"endstream", m.end())])
    return destino


# ---------------------------------------------------------------- selección
PVC_ANTIGUAS = f("pvc", "1792047083452.jpg", "1792047083532.jpg", "1792047083837.jpg", "1792047083940.jpg", "1792047084029.jpg")
FIELTRO_ANTIGUAS = f("fieltro", "1792047079196.jpg", "1792047079022.jpg", "1792047079144.jpg")

PRODUCTOS = {
    # --- elevación (fotos de la web anterior)
    ("elevacion", "bandas-elevadoras"): ant(*(f"productos/elevacion/bandas-elevadoras-0{n}.jpg" for n in (5, 6, 4, 7))),
    ("elevacion", "cangilones"): ant(*(f"productos/elevacion/cangilones-0{n}.jpg" for n in (1, 5, 6, 2))),
    ("elevacion", "imanes"): ant("productos/elevacion/imanes-05.jpg"),
    ("elevacion", "paneles-de-explosion"): ant("productos/elevacion/paneles-de-explosion-05.jpg",
                                               "productos/elevacion/paneles-de-explosion-03.jpg"),
    # --- bandas transportadoras
    ("bandas-transportadoras", "bandas-transportadoras"): f("goma", "IMG-20261022-WA0065.jpg")
        + ant(*(f"productos/bandas-transportadoras/bandas-transportadoras-{n}.jpg" for n in ("12", "07", "06", "08", "10"))),
    ("bandas-transportadoras", "vulcanizados"): ant(*(f"productos/bandas-transportadoras/vulcanizados-0{n}.jpg" for n in (2, 3, 8, 6))),
    ("bandas-transportadoras", "materiales-para-vulcanizar"): ant(
        *(f"productos/bandas-transportadoras/materiales-para-vulcanizar-0{n}.jpg" for n in (9, 8))),
    ("bandas-transportadoras", "planchas-de-goma"): f("goma blanda", "IMG-20261022-WA0048.jpg")
        + ant(*(f"productos/bandas-transportadoras/planchas-de-goma-0{n}.jpg" for n in (5, 4, 6))),
    ("bandas-transportadoras", "rodillos"): ant("productos/bandas-transportadoras/rodillos-01.jpg"),
    # --- componentes para vibradores
    ("faldetas", "faldetas"): [jpeg_de_pdf(ref("COMPONENTES PARA VIBRADORES", "Faldetas – CRM – Componentes.pdf"))]
        + f("goma", "IMG-20261022-WA0042.jpg") + f("goma verde", "IMG-20261022-WA0067.jpg")
        + f("fieltro", "IMG-20261022-WA0050.jpg") + f("caramelo", "1792047084526.jpg") + f("borde ondulado", "1792047083023.jpg"),
    ("faldetas", "goma"): f("goma", *(f"IMG-20261022-WA00{n}.jpg" for n in (42, 21, 41, 43, 31, 57, 55)))
        + f("goma verde", "IMG-20261022-WA0067.jpg", "IMG-20261022-WA0023.jpg", "IMG-20261022-WA0049.jpg")
        + f("goma", "1792047082621.jpg", "1792047082653.jpg"),
    ("faldetas", "fieltro"): f("fieltro", *(f"IMG-20261022-WA00{n}.jpg" for n in (50, 33, 35, 63, 32, 56))) + FIELTRO_ANTIGUAS,
    ("faldetas", "caramelo"): f("caramelo", "1792047084526.jpg", "1792047084365.jpg", "1792047084578.jpg",
                                "1792047084627.jpg", "1792047084418.jpg"),
    ("faldetas", "estrellas"): f("estrellas", *(f"IMG-20261022-WA00{n}.jpg" for n in (58, 66, 46, 44, 60, 47)))
        + f("goma verde", "IMG-20261022-WA0062.jpg")
        + f("estrellas", "1792047083289.jpg", "1792047084071.jpg", "1792047084140.jpg"),
    ("faldetas", "piezas-de-goma"): ant("productos/faldetas/piezas-de-goma-11.jpg", "productos/faldetas/piezas-de-goma-10.jpg"),
    ("faldetas", "tacos"): f("tacos", "1792047082919.jpg", "1792047082865.jpg", "1792047082846.jpg")
        + ant("productos/faldetas/tacos-04.jpg"),
    ("faldetas", "borde-ondulado"): f("borde ondulado", "1792047083023.jpg", "1792047083064.jpg", "1792047082960.jpg"),
    ("faldetas", "red"): f("red(nuevo producto dentro de faldetas)", "1792047085865.jpg"),
    # --- bandas PVC
    ("bandas-pvc", "bandas-de-pvc"): f("pvc", *(f"IMG-20261022-WA00{n}.jpg" for n in ("53", "61", "37", "38", "36", "39", "19")))
        + [ref("PVC", "20230425_163616.jpg"), ref("PVC", "IMG-20230424-WA0034.jpg")] + PVC_ANTIGUAS,
    ("bandas-pvc", "bandas-modulares"): ant("productos/bandas-pvc/bandas-modulares-06.jpg", "productos/bandas-pvc/bandas-modulares-05.jpg"),
    ("bandas-pvc", "cordones-y-correas"): ant("productos/bandas-pvc/cordones-y-correas-02.jpg",
                                              "productos/bandas-pvc/cordones-y-correas-03.jpg"),
    ("bandas-pvc", "recubrimientos"): [ref("PVC", "IMG-20230424-WA0064.jpg"), ref("PVC", "IMG-20230424-WA0065.jpg")],
    ("bandas-pvc", "grapas"): f("pvc", "1792047085348.jpg", "1792047085411.jpg", "1792047085108.jpg",
                                "1792047084997.jpg", "1792047085071.jpg") + ant("productos/bandas-pvc/grapas-07.jpg"),
}
EMPRESA = {
    "fachada": f("nave nueva", "1792047078821.jpg")[0],
    "nave-nueva-1": f("nave nueva", "1792047079777.jpg")[0],
    "nave-nueva-2": f("nave nueva", "1792047079519.jpg")[0],
    "cnc-1": f("maquina cnc", "1792047083386.jpg")[0],
    "cnc-2": f("maquina cnc", "1792047083419.jpg")[0],
    "alta-frecuencia-1": f("pvc", "1792047084816.jpg")[0],
    "alta-frecuencia-2": f("pvc", "1792047084723.jpg")[0],
    "corte-cnc-goma": f("goma", "1792047083163.jpg")[0],
    "troqueladora": f("estrellas", "IMG-20261022-WA0054.jpg")[0],
    "prensa-fieltro": f("fieltro", "IMG-20261022-WA0007.jpg")[0],
    "planchas-1": ref("PORTADA", "FOTOS GARANTIA DE SATISFACION", "ea656808-0f39-414c-8a4f-1ad318fbfb96.jpg"),
    "planchas-2": ref("PORTADA", "FOTOS GARANTIA DE SATISFACION", "45825f85-56c1-4ae9-9d1f-3f407adb661d.jpg"),
    "oficinas": ant("noticias/nuevas-oficinas-crm-01.jpg")[0],
    # Envíos: fotos sin el nombre del transportista (la 2 está recortada para dejar fuera el rótulo del remolque)
    "transporte-1": f("transporte", "1793260136481.jpg")[0],
    "transporte-2": recortada(f("transporte", "1793260132639.jpg")[0], (0, 0.08, 0.575, 1)),
    "transporte-3": f("transporte", "1793260135549.jpg")[0],
}
SECTORES = {  # franja de sectores, páginas /sectores/ y campañas de la portada (fotos de Pexels, licencia libre)
    "olivar": f("olivo aceituna", "pexels-hani-salama-195685919.jpg")[0],
    "olivar-campo": f("fotos de fondo", "1792047079926.jpg")[0],      # olivo con camino (foto propia)
    "almendro": f("almendra", "pexels-shutterpicks-3632381.jpg")[0],
    "almendro-flor": f("almendra", "pexels-epistolo-11086132.jpg")[0],
    "ajos": f("ajos", "pexels-rachael-holzman-34339.jpg")[0],
    "ajo-campo": f("ajos", "pexels-juan-moccagatta-21594.jpg")[0],
    "trigo": f("trigo", "pexels-darya-grey_owl-132130.jpg")[0],
    "industria": ant("productos/bandas-transportadoras/bandas-transportadoras-04.jpg")[0],
}
FONDOS = {
    "campo": f("fotos de fondo", "1792047081979.jpg")[0],
}
VIDEOS = {
    # nombre: (archivo, segundo de inicio, duración)
    "corte-fieltro": ("VID_20201011_195533.mp4", 0, 20),
    # Vídeo vertical: se recorta una franja panorámica a la altura de los cabezales (y=380 px)
    "corte-cnc": ("maquina cnc/VID_20250324_115641.mp4", 0, 18),
}


def foto(origen, destino, lado_max=1400, calidad=78):
    return procesar(origen, destino, lado_max, calidad)


# Los nombres reales de los archivos de fotos de Pexels varían en el sufijo: se resuelven por prefijo
def resolver(ruta):
    if os.path.exists(ruta):
        return ruta
    carpeta, nombre = os.path.split(ruta)
    base = os.path.splitext(nombre)[0]
    candidatos = [n for n in os.listdir(carpeta) if n.startswith(base)]
    if len(candidatos) != 1:
        raise FileNotFoundError(ruta)
    return os.path.join(carpeta, candidatos[0])


total = 0
n = 0
for (cat, fam), fotos in PRODUCTOS.items():
    carpeta = os.path.join(REPO, "assets", "img", "productos", cat, fam)
    shutil.rmtree(carpeta, ignore_errors=True)
    for i, ruta in enumerate(fotos, 1):
        total += foto(resolver(ruta), os.path.join(carpeta, f"{i:02d}.webp"))
        n += 1
    print(f"productos/{cat}/{fam}: {len(fotos)} fotos")

for nombre, ruta in EMPRESA.items():
    total += foto(resolver(ruta), os.path.join(REPO, "assets", "img", "empresa", f"{nombre}.webp"))
    n += 1
print(f"empresa: {len(EMPRESA)} fotos")

for nombre, ruta in SECTORES.items():
    total += foto(resolver(ruta), os.path.join(REPO, "assets", "img", "sectores", f"{nombre}.webp"), lado_max=1600)
    n += 1
print(f"sectores: {len(SECTORES)} fotos")

for nombre, ruta in FONDOS.items():
    total += foto(resolver(ruta), os.path.join(REPO, "assets", "img", "fondos", f"{nombre}.webp"), lado_max=2400, calidad=80)
    n += 1
print(f"fondos: {len(FONDOS)} fotos")

vdir = os.path.join(REPO, "assets", "video")
os.makedirs(vdir, exist_ok=True)
for nombre, (archivo, ini, dur) in VIDEOS.items():
    entrada = os.path.join(SRC, archivo)
    vertical = "cnc" in nombre   # recorte panorámico (16:9) a la altura de la herramienta
    salida = os.path.join(vdir, f"{nombre}.mp4")
    if not os.path.exists(salida) or "--videos" in sys.argv:
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-t", str(dur), "-i", entrada,
            "-an", "-vf", ("crop=iw:iw*9/16:0:380," if vertical else "") + "scale=-2:720,fps=30", "-c:v", "libx264", "-preset", "slow", "-crf", "28",
            "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", salida,
        ], check=True)
    fotograma = os.path.join(vdir, f"{nombre}-fotograma.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", salida, "-frames:v", "1", fotograma], check=True)
    poster = os.path.join(vdir, f"{nombre}.webp")
    procesar(fotograma, poster, lado_max=1280, calidad=75)
    os.remove(fotograma)
    total += os.path.getsize(salida) + os.path.getsize(poster)
    print(f"vídeo {nombre}: {os.path.getsize(salida) / 1e6:.1f} MB")

print(f"TOTAL: {n} fotos + {len(VIDEOS)} vídeos = {total / 1e6:.1f} MB")
