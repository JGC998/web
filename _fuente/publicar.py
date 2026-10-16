"""Regenera la web, la comprueba y la sube a GitHub (Cloudflare la publica en 1-2 minutos).

Uso: doble clic en _fuente/publicar.bat   (o:  py _fuente/publicar.py)
"""
import os, subprocess, sys

FUENTE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(FUENTE)
os.chdir(REPO)


def paso(texto):
    print(f"\n== {texto}")


def ejecutar(cmd, **kw):
    return subprocess.run(cmd, text=True, encoding="utf-8", errors="replace", **kw)


paso("1/4 Generando las páginas (y convirtiendo fotos nuevas)…")
if ejecutar([sys.executable, os.path.join(FUENTE, "construir.py")], capture_output=True).returncode != 0:
    r = ejecutar([sys.executable, os.path.join(FUENTE, "construir.py")])
    sys.exit("No se ha podido generar la web. Revisa el mensaje de arriba (¿falta 'titulo:' o 'fecha:' en una noticia?).")
print("   Hecho.")

paso("2/4 Comprobando enlaces e imágenes…")
r = ejecutar([sys.executable, os.path.join(FUENTE, "herramientas", "comprobar.py")], capture_output=True)
print("   " + r.stdout.strip().replace("\n", "\n   "))
if "rotos: 0" not in r.stdout:
    sys.exit("Hay enlaces rotos: no se publica. Revisa la lista de arriba.")

paso("3/4 Guardando los cambios…")
ejecutar(["git", "add", "-A"])
if ejecutar(["git", "diff", "--cached", "--quiet"]).returncode == 0:
    print("   No hay cambios que publicar.")
    sys.exit(0)
cambios = ejecutar(["git", "diff", "--cached", "--name-only"], capture_output=True).stdout.split()
noticias = sorted({c.split("/")[1] for c in cambios if c.startswith("noticias/") and c.count("/") >= 2})
mensaje = "Publicar noticias: " + ", ".join(noticias) if noticias else "Actualizar la web"
ejecutar(["git", "commit", "-q", "-m", mensaje])
print(f"   {mensaje} ({len(cambios)} archivos)")

paso("4/4 Subiendo a GitHub…")
if ejecutar(["git", "push", "-q"]).returncode != 0:
    sys.exit("No se ha podido subir. ¿Hay conexión a internet? Los cambios están guardados; vuelve a intentarlo.")
print("   Subido. La web se actualizará en 1-2 minutos.")
