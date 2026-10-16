"""Comprueba que no haya enlaces internos rotos ni imágenes sin usar.

Uso (desde la raíz del proyecto):  py _fuente/herramientas/comprobar.py
"""
import re, glob, os

os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

BS = chr(92)  # barra invertida de Windows


def norm(p):
    return p.replace(BS, "/")


files = [norm(f) for f in glob.glob("**/*.html", recursive=True) if not norm(f).startswith(("_fuente/", "web fotos/", "fotos-antiguas/"))]
css = [norm(f) for f in glob.glob("**/*.css", recursive=True)]
bad = 0
used = set()
for f in files + css:
    t = open(f, encoding="utf-8").read()
    refs = re.findall(r'(?:href|src|content)="(/[^"#?]*)', t) + re.findall(r"url\('?(/[^')]+)'?\)", t)
    # og:image y similares llevan el dominio delante: https://dominio/assets/...
    refs += re.findall(r'content="https?://[^/"]+(/assets/[^"#?]*)', t)
    for u in refs:
        p = u.lstrip("/")
        if p == "" or p.endswith("/"):
            p += "index.html"
        used.add(p)
        if f.endswith(".html") and not os.path.exists(p):
            bad += 1
            print("ROTO", f, u)
print("html:", len(files), "rotos:", bad)

imgs = [norm(i) for i in glob.glob("assets/img/**/*.*", recursive=True)]
imgs = [i for i in imgs if "/thumbs/" not in i]
unused = [i for i in imgs if i not in used and os.path.dirname(i) + "/thumbs/" + os.path.basename(i) not in used]
print("sin usar:", len(unused))
for u in unused:
    print("  ", u)
