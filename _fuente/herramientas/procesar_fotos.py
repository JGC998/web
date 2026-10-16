"""Procesa las fotos y vídeos originales de 'web fotos/' para la web.

- Fotos: enderezadas (EXIF), recortadas al tamaño web, JPG progresivo y SIN metadatos
  (se elimina la ubicación GPS del móvil).
- Vídeos: H.264 720p sin sonido, optimizados para empezar a reproducirse enseguida,
  más una imagen fija (poster).

Uso (desde la raíz del proyecto):  py _fuente/herramientas/procesar_fotos.py
La selección de fotos de cada familia se define abajo (PRODUCTOS, EMPRESA, FONDOS, VIDEOS).
"""
import os, sys, subprocess, shutil
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None  # fotos de 200 MP del móvil

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "web fotos")


def lista(carpeta):
    return sorted(f for f in os.listdir(os.path.join(SRC, carpeta)) if f.lower().endswith(".jpg"))


def pick(carpeta, numeros):
    """Fotos elegidas por su número en la hoja de contactos (1 = primera)."""
    fs = lista(carpeta)
    return [os.path.join(carpeta, fs[n - 1]) for n in numeros]


# ---------------------------------------------------------------- selección
PRODUCTOS = {
    ("bandas-pvc", "bandas-de-pvc"): pick("pvc", [1, 3, 9, 11, 13, 6, 27, 28, 29, 30, 31, 22]),
    ("bandas-pvc", "grapas"): pick("pvc", [25, 26, 20, 17, 19]),
    ("faldetas", "faldetas"): pick("goma", [2]) + pick("caramelo", [4]) + pick("fieltro", [4]) + pick("borde ondulado", [3]),
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
}
FONDOS = {
    "campo": pick("fotos de fondo", [8])[0],
}
VIDEOS = {
    # nombre: (archivo, segundo de inicio, duración)
    "corte-fieltro": ("VID_20201011_195533.mp4", 0, 20),
    "corte-cnc": ("maquina cnc/VID_20250324_115712.mp4", 0, 14),
}


def foto(origen, destino, lado_max=1400, calidad=76):
    im = Image.open(os.path.join(SRC, origen))
    im.draft("RGB", (lado_max * 2, lado_max * 2))  # decodificación rápida de JPG enormes
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((lado_max, lado_max), Image.LANCZOS)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    im.save(destino, "JPEG", quality=calidad, optimize=True, progressive=True)  # sin EXIF
    return os.path.getsize(destino)


total = 0
n = 0
for (cat, fam), fotos in PRODUCTOS.items():
    carpeta = os.path.join(REPO, "assets", "img", "productos", cat, fam)
    shutil.rmtree(carpeta, ignore_errors=True)
    for i, f in enumerate(fotos, 1):
        total += foto(f, os.path.join(carpeta, f"{i:02d}.jpg"))
        n += 1
    print(f"productos/{cat}/{fam}: {len(fotos)} fotos")

for nombre, f in EMPRESA.items():
    total += foto(f, os.path.join(REPO, "assets", "img", "empresa", f"{nombre}.jpg"))
    n += 1
print(f"empresa: {len(EMPRESA)} fotos")

for nombre, f in FONDOS.items():
    total += foto(f, os.path.join(REPO, "assets", "img", "fondos", f"{nombre}.jpg"), lado_max=2400, calidad=78)
    n += 1
print(f"fondos: {len(FONDOS)} fotos")

vdir = os.path.join(REPO, "assets", "video")
os.makedirs(vdir, exist_ok=True)
for nombre, (f, ini, dur) in VIDEOS.items():
    entrada = os.path.join(SRC, f)
    # Los vídeos grabados en vertical se recortan a panorámico (16:9) por el centro
    vertical = "cnc" in nombre
    salida = os.path.join(vdir, f"{nombre}.mp4")
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-t", str(dur), "-i", entrada,
        "-an", "-vf", ("crop=iw:iw*9/16," if vertical else "") + "scale=-2:720,fps=30", "-c:v", "libx264", "-preset", "slow", "-crf", "28",
        "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", salida,
    ], check=True)
    poster = os.path.join(vdir, f"{nombre}.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", salida, "-frames:v", "1", "-q:v", "4", poster], check=True)
    total += os.path.getsize(salida) + os.path.getsize(poster)
    print(f"vídeo {nombre}: {os.path.getsize(salida) / 1e6:.1f} MB")

print(f"TOTAL: {n} fotos + {len(VIDEOS)} vídeos = {total / 1e6:.1f} MB")
