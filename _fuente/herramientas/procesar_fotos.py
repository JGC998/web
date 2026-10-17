"""Procesa las fotos y vídeos originales de 'web fotos/' para la web.

- Fotos: enderezadas (EXIF), recortadas al tamaño web, JPG progresivo y SIN metadatos
  (se elimina la ubicación GPS del móvil).
- Vídeos: H.264 720p sin sonido, optimizados para empezar a reproducirse enseguida,
  más una imagen fija (poster).

Uso (desde la raíz del proyecto):  py _fuente/herramientas/procesar_fotos.py
La selección de fotos de cada familia se define abajo (PRODUCTOS, EMPRESA, FONDOS, VIDEOS).
"""
import os, re, sys, subprocess, shutil, tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imagenes import procesar  # WebP sin metadatos


REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "web fotos")
REF = os.path.join(REPO, "WEB NUEVA 2026")   # material del borrador de on3d (noviembre 2025)


def ref(*ruta):
    """Foto de 'WEB NUEVA 2026/' (ruta absoluta: os.path.join(SRC, ...) la respeta)."""
    return os.path.join(REF, *ruta)


def jpeg_de_pdf(pdf):
    """Extrae la foto incrustada en un PDF (la de faldetas viene dentro de un PDF). Se queda con el
    JPEG que más ocupa: el PDF lleva además un recuadro en blanco que es más grande pero casi vacío."""
    datos = open(pdf, "rb").read()
    fotos = [m for m in re.finditer(rb"<<(.{0,600}?)>>\s*stream\r?\n", datos, re.S) if b"DCTDecode" in m.group(1)]
    m = max(fotos, key=lambda m: datos.find(b"endstream", m.end()) - m.end())
    destino = os.path.join(tempfile.gettempdir(), "crm-" + os.path.basename(pdf) + ".jpg")
    open(destino, "wb").write(datos[m.end():datos.find(b"endstream", m.end())])
    return destino


def lista(carpeta):
    return sorted(f for f in os.listdir(os.path.join(SRC, carpeta)) if f.lower().endswith(".jpg"))


def pick(carpeta, numeros):
    """Fotos elegidas por su número en la hoja de contactos (1 = primera)."""
    fs = lista(carpeta)
    return [os.path.join(carpeta, fs[n - 1]) for n in numeros]


# ---------------------------------------------------------------- selección
PRODUCTOS = {
    ("bandas-pvc", "bandas-de-pvc"): pick("pvc", [1, 3, 9, 11, 13, 6, 27, 28, 29, 30, 31, 22])
        + [ref("PVC", f) for f in ["20230425_163616.jpg", "IMG-20230424-WA0034.jpg", "IMG-20230424-WA0046.jpg",
                                   "IMG-20230424-WA0080.jpg", "IMG-20230424-WA0049.jpg"]],
    ("bandas-pvc", "recubrimientos"): [ref("PVC", "IMG-20230424-WA0064.jpg"), ref("PVC", "IMG-20230424-WA0065.jpg")],
    ("bandas-transportadoras", "bandas-transportadoras"): [ref("BANDAS TRANSPORTADORAS", "BANER.jpg"),
                                                           ref("BANDAS TRANSPORTADORAS", "BANER 32.jpg")],
    ("bandas-pvc", "grapas"): pick("pvc", [25, 26, 20, 17, 19]),
    ("faldetas", "faldetas"): [jpeg_de_pdf(ref("COMPONENTES PARA VIBRADORES", "Faldetas – CRM – Componentes.pdf"))]
        + pick("goma", [2]) + pick("caramelo", [4]) + pick("fieltro", [4]) + pick("borde ondulado", [3]),
    ("faldetas", "caramelo"): pick("caramelo", [4, 1, 5, 6, 2]),
    ("faldetas", "fieltro"): pick("fieltro", [4, 1, 3, 5, 7, 9, 10, 11]),
    ("faldetas", "goma"): pick("goma", [2, 3, 8, 9, 5, 6, 7, 10, 11]),
    ("faldetas", "tacos"): pick("tacos", [3, 2, 1]),
    ("faldetas", "estrellas"): pick("estrellas", [2, 4, 6, 7, 9, 10, 11, 12]),
    ("faldetas", "borde-ondulado"): pick("borde ondulado", [3, 4, 1]),
    ("faldetas", "red"): pick("red(nuevo producto dentro de faldetas)", [1]),
}
EMPRESA = {
    "fachada": pick("nave nueva", [1])[0],
    "nave-nueva-1": pick("nave nueva", [9])[0],
    "nave-nueva-2": pick("nave nueva", [3])[0],
    "cnc-1": pick("maquina cnc", [2])[0],
    "cnc-2": pick("maquina cnc", [3])[0],
    "alta-frecuencia-1": pick("pvc", [16])[0],
    "alta-frecuencia-2": pick("pvc", [14])[0],
    "corte-cnc-goma": pick("goma", [5])[0],
    "planchas-1": ref("PORTADA", "FOTOS GARANTIA DE SATISFACION", "ea656808-0f39-414c-8a4f-1ad318fbfb96.jpg"),
    "planchas-2": ref("PORTADA", "FOTOS GARANTIA DE SATISFACION", "45825f85-56c1-4ae9-9d1f-3f407adb661d.jpg"),
}
SECTORES = {  # franja "Sectores" de la portada
    "olivar": ref("PORTADA", "FOTOS BANER", "OLIVAR.jpg"),
    "girasol": ref("PORTADA", "FOTOS BANER", "4755e41b-30be-4391-8f06-ffb60381a17a.jpg"),
    "ajos": ref("PORTADA", "FOTOS BANER", "AJOS.jpg"),
}
CATEGORIAS = {  # foto que aparece al pasar el ratón por la tarjeta de la categoría (solo las que no tienen fotos de producto)
    "elevacion": ref("ELEVACION", "BANER ELEVACION.JPG"),
}
FONDOS = {
    "campo": pick("fotos de fondo", [8])[0],
}
VIDEOS = {
    # nombre: (archivo, segundo de inicio, duración)
    "corte-fieltro": ("VID_20201011_195533.mp4", 0, 20),
    # Vídeo vertical: se recorta una franja panorámica a la altura de los cabezales (y=380 px)
    "corte-cnc": ("maquina cnc/VID_20250324_115641.mp4", 0, 18),
}


def foto(origen, destino, lado_max=1400, calidad=78):
    return procesar(os.path.join(SRC, origen), destino, lado_max, calidad)


total = 0
n = 0
for (cat, fam), fotos in PRODUCTOS.items():
    carpeta = os.path.join(REPO, "assets", "img", "productos", cat, fam)
    shutil.rmtree(carpeta, ignore_errors=True)
    for i, f in enumerate(fotos, 1):
        total += foto(f, os.path.join(carpeta, f"{i:02d}.webp"))
        n += 1
    print(f"productos/{cat}/{fam}: {len(fotos)} fotos")

for nombre, f in EMPRESA.items():
    total += foto(f, os.path.join(REPO, "assets", "img", "empresa", f"{nombre}.webp"))
    n += 1
print(f"empresa: {len(EMPRESA)} fotos")

for nombre, f in SECTORES.items():
    total += foto(f, os.path.join(REPO, "assets", "img", "sectores", f"{nombre}.webp"), lado_max=1200)
    n += 1
print(f"sectores: {len(SECTORES)} fotos")

for nombre, f in CATEGORIAS.items():
    total += foto(f, os.path.join(REPO, "assets", "img", "categorias", f"{nombre}.webp"), lado_max=900, calidad=80)
    n += 1
print(f"categorías: {len(CATEGORIAS)} fotos")

for nombre, f in FONDOS.items():
    total += foto(f, os.path.join(REPO, "assets", "img", "fondos", f"{nombre}.webp"), lado_max=2400, calidad=80)
    n += 1
print(f"fondos: {len(FONDOS)} fotos")

vdir = os.path.join(REPO, "assets", "video")
os.makedirs(vdir, exist_ok=True)
for nombre, (f, ini, dur) in VIDEOS.items():
    entrada = os.path.join(SRC, f)
    # Los vídeos grabados en vertical se recortan a panorámico (16:9) por el centro
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
