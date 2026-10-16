"""Procesado de fotos para la web: enderezar, reducir y guardar en WebP sin metadatos.

WebP pesa en torno a un 30 % menos que JPG con la misma calidad, y lo entienden
todos los navegadores actuales (también móviles Android antiguos).
Al guardar no se copia el EXIF, así que se elimina la ubicación GPS del móvil.
"""
import os
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None  # fotos de 200 MP de algunos móviles

EXTENSIONES = (".jpg", ".jpeg", ".png", ".webp")


def es_foto(nombre):
    return nombre.lower().endswith(EXTENSIONES) and not nombre.startswith(".")


def procesar(origen, destino, lado_max=1400, calidad=78):
    """Convierte 'origen' en un WebP de como máximo lado_max píxeles. Devuelve el tamaño en bytes."""
    im = Image.open(origen)
    im.draft("RGB", (lado_max * 2, lado_max * 2))  # lectura rápida de JPG enormes
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((lado_max, lado_max), Image.LANCZOS)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    im.save(destino, "WEBP", quality=calidad, method=6)
    return os.path.getsize(destino)
