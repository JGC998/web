"""Borra un logotipo rojo de una superficie clara (el lateral blanco de un remolque).

Solo se sustituyen los píxeles rojos dentro de las zonas indicadas: cada uno toma el color
del panel que lo rodea en su misma fila (interpolando entre el píxel limpio más cercano a
la izquierda y a la derecha). Las partes blancas del logo, las sombras y los reflejos del
panel se conservan tal cual, así que el arreglo no se nota a tamaño web.
"""
from PIL import Image, ImageFilter


def _rojo(p, margen):
    r, g, b = p[:3]
    return r > g + margen and r > b + margen


def borrar(im, zonas, margen=26, dilatar=3):
    """im: imagen RGB (se modifica). zonas: lista de (x0, y0, x1, y1) en píxeles de im."""
    px = im.load()
    w, h = im.size
    for x0, y0, x1, y1 in zonas:
        # 1) máscara de píxeles rojos, ampliada unos píxeles para cubrir el antialiasing
        rojos = {(x, y) for y in range(y0, y1) for x in range(x0, x1) if _rojo(px[x, y], margen)}
        mascara = set()
        for x, y in rojos:
            for dy in range(-dilatar, dilatar + 1):
                for dx in range(-dilatar, dilatar + 1):
                    if x0 <= x + dx < x1 and y0 <= y + dy < y1:
                        mascara.add((x + dx, y + dy))
        # 2) relleno fila a fila desde el píxel limpio más cercano a cada lado
        for y in range(y0, y1):
            fila = [x for x in range(x0, x1) if (x, y) in mascara]
            if not fila:
                continue
            tramo_ini = fila[0]
            for i, x in enumerate(fila):
                fin_de_tramo = i == len(fila) - 1 or fila[i + 1] != x + 1
                if not fin_de_tramo:
                    continue
                a, b = tramo_ini - 1, x + 1          # píxeles limpios que rodean el tramo
                a, b = max(a, 0), min(b, w - 1)
                ca, cb = px[a, y], px[b, y]
                n = b - a
                for xx in range(tramo_ini, x + 1):
                    t = (xx - a) / n
                    px[xx, y] = tuple(round(ca[k] * (1 - t) + cb[k] * t) for k in range(3))
                if i + 1 < len(fila):
                    tramo_ini = fila[i + 1]
        # 3) suavizado solo de lo rellenado, para que no queden rayas horizontales
        caja = (max(x0 - 4, 0), max(y0 - 4, 0), min(x1 + 4, w), min(y1 + 4, h))
        suave = im.crop(caja).filter(ImageFilter.GaussianBlur(2.2))
        sp = suave.load()
        for x, y in mascara:
            px[x, y] = sp[x - caja[0], y - caja[1]]
    return im
