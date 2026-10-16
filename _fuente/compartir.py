"""Imágenes para compartir (las que salen al enviar un enlace por WhatsApp o redes).

Genera un JPG de 1200×630 con una foto de fondo (o el verde de CRM), el logo,
el título de la página y una frase. JPG porque es el formato que aceptan
todas las apps de mensajería al mostrar la vista previa.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

FUENTE = os.path.dirname(os.path.abspath(__file__))
W, H = 1200, 630
VERDE_OSCURO, VERDE = (16, 82, 30), (46, 146, 51)


def _fuente(peso, tam):
    return ImageFont.truetype(os.path.join(FUENTE, "fuentes", f"Inter-{peso}.ttf"), tam)


def _lineas(draw, texto, fuente, ancho):
    """Reparte el texto en líneas que quepan en 'ancho'."""
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = f"{actual} {p}".strip()
        if draw.textlength(prueba, font=fuente) <= ancho:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    return lineas + [actual]


def _fondo(foto):
    if foto:
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(foto)).convert("RGB"), (W, H), Image.LANCZOS)
        velo = Image.new("L", (W, H))
        dv = ImageDraw.Draw(velo)
        for x in range(W):  # más oscuro a la izquierda, donde va el texto
            dv.line([(x, 0), (x, H)], fill=int(205 - 95 * x / W))
        return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, velo)
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for x in range(W):  # degradado verde de la marca
        t = x / W
        d.line([(x, 0), (x, H)], fill=tuple(int(a + (b - a) * t) for a, b in zip(VERDE_OSCURO, VERDE)))
    return im


def generar(destino, titulo, frase, foto=None, logo=None):
    im = _fondo(foto)
    d = ImageDraw.Draw(im)
    x = 72
    if logo:  # logo sobre una pastilla blanca, arriba a la izquierda
        lg = Image.open(logo).convert("RGBA")
        lg.thumbnail((190, 66), Image.LANCZOS)
        d.rounded_rectangle([x - 22, 56, x + lg.width + 22, 56 + lg.height + 24], radius=18, fill=(255, 255, 255))
        im.paste(lg, (x, 68), lg)
    f_tit, f_frase = _fuente("Bold", 68), _fuente("Regular", 32)
    lineas = _lineas(d, titulo, f_tit, W - 2 * x)[:3]
    alto = len(lineas) * 78 + (56 if frase else 0)
    y = H - 72 - alto
    for l in lineas:
        d.text((x, y), l, font=f_tit, fill=(255, 255, 255))
        y += 78
    if frase:
        d.text((x, y + 14), _lineas(d, frase, f_frase, W - 2 * x)[0], font=f_frase, fill=(225, 238, 226))
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    im.save(destino, "JPEG", quality=84, optimize=True, progressive=True)
