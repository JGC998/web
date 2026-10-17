"""Genera todas las páginas de la web de CRM a partir de _fuente/.

Uso (desde la carpeta raíz del proyecto):
    py _fuente/construir.py

Lee:
  _fuente/contenido/productos.json        categorías y familias de producto
  _fuente/contenido/textos_productos.py   textos técnicos y tablas
  _fuente/contenido/legal.json            textos legales
  _fuente/contenido/noticias-archivo.json noticias antiguas
  assets/img/productos/<cat>/<familia>/   fotos de cada carrusel
y escribe los index.html de cada página.
"""
import sys, os, json, html, urllib.parse

FUENTE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(FUENTE)
sys.path.insert(0, FUENTE)
sys.path.insert(0, os.path.join(FUENTE, "contenido"))

from PIL import Image
from iconos import ICONS, icon, badge
from textos_productos import TEXT, EXTRA
from sectores import SECTORES
import idiomas as I
from noticias import leer_noticias, fecha_larga
from compartir import generar as generar_imagen_compartir

e = html.escape

# ---------------------------------------------------------------- datos de la empresa
# Dominio donde está publicada la web. Se usa en el sitemap, robots.txt y las imágenes
# para compartir. Cuando se migre el dominio, cambiar a "https://crmsl.es" y regenerar.
SITE = "https://crmgestiontaller.com"
PHONE = "+34 957 682 819"
PHONE_TEL = "+34957682819"
EMAIL = "info@crmsl.es"
WHATSAPP = "34656844067"          # móvil con prefijo de país, sin + ni espacios
WHATSAPP_VER = "656 84 40 67"


def presupuesto(producto=""):
    """Enlace al formulario de presupuesto con el producto ya seleccionado."""
    return "/presupuesto/" + (f"?producto={urllib.parse.quote(producto)}" if producto else "")


def wa(texto="Hola, quería hacer una consulta."):
    """Enlace a WhatsApp con el mensaje ya escrito."""
    return f"https://wa.me/{WHATSAPP}?text={urllib.parse.quote(texto)}"
VERSION = "20261017e"
# Estadísticas de visitas (Cloudflare Web Analytics: sin cookies). Vacío = desactivado.
ANALITICA_TOKEN = "c9bd8190b2be4939ae6689fd3909c441"   # súbelo al cambiar CSS o JS para que los navegadores los descarguen de nuevo

# ---------------------------------------------------------------- contenido
_P = json.load(open(os.path.join(FUENTE, "contenido", "productos.json"), encoding="utf-8"))
CATEGORIAS = _P["categorias"]
# Familias con "oculta": true en productos.json no se publican (se conservan sus datos y fotos)
for _c in CATEGORIAS:
    _c["familias"] = [f for f in _c["familias"] if not f.get("oculta")]
PRODUCTS = [(c["slug"], c["nombre"], c["intro"]) for c in CATEGORIAS]   # orden del menú
NAMES = {c["slug"]: c["nombre"] for c in CATEGORIAS}
SHORT = {c["slug"]: c["corto"] for c in CATEGORIAS}
NAMES_EN = {c["slug"]: c["nombre_en"] for c in CATEGORIAS}
SHORT_EN = {c["slug"]: c["corto_en"] for c in CATEGORIAS}

# Páginas que existen en los dos idiomas (para el enlace English/Español y hreflang)
PAGINA_IDIOMA = {ruta: clave for rutas in I.RUTAS.values() for clave, ruta in rutas.items()}   # ruta -> página
CAT_ICON = {c["slug"]: c["icono"] for c in CATEGORIAS}
SEC_ICON = {c["slug"]: {f["slug"]: f["icono"] for f in c["familias"]} for c in CATEGORIAS}
C = {"products": {c["slug"]: [{"slug": f["slug"], "title": f["nombre"]} for f in c["familias"]] for c in CATEGORIAS}}
LEGAL = json.load(open(os.path.join(FUENTE, "contenido", "legal.json"), encoding="utf-8"))
from legal_textos import TEXTOS as _LEGAL_NUEVOS   # textos legales actualizados y aprobados (octubre 2026)
LEGAL.update(_LEGAL_NUEVOS)
ARCHIVO_NOTICIAS = json.load(open(os.path.join(FUENTE, "contenido", "noticias-archivo.json"), encoding="utf-8"))
NOTICIAS = leer_noticias(FUENTE, REPO)   # carpetas de _fuente/contenido/noticias/
PAGINAS = []                             # rutas generadas, para el sitemap


def img_size(rel):
    with Image.open(os.path.join(REPO, rel)) as im:
        return im.size


ANCHOS = (480, 800, 1100)   # copias reducidas para pantallas pequeñas (assets/img/tamanos/)


def copias(rel, w):
    """Crea (si faltan o están anticuadas) las copias reducidas de una foto y devuelve el srcset."""
    origen = os.path.join(REPO, rel)
    partes = []
    for ancho in (a for a in ANCHOS if a < w * 0.9):
        copia = "assets/img/tamanos/" + rel[len("assets/img/"):].replace(".webp", f"-{ancho}.webp")
        ruta = os.path.join(REPO, copia)
        if not os.path.exists(ruta) or os.path.getmtime(ruta) < os.path.getmtime(origen):
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            with Image.open(origen) as im:
                im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS).save(ruta, "WEBP", quality=78, method=6)
        partes.append(f"/{copia} {ancho}w")
    return ", ".join(partes + [f"/{rel} {w}w"]) if partes else ""


def img(rel, alt, cls="", lazy=True, sizes="(max-width: 1240px) 100vw, 1200px"):
    """sizes: ancho con el que se pinta la foto, para que el móvil descargue la copia pequeña."""
    w, h = img_size(rel)
    a = f' class="{cls}"' if cls else ""
    l = ' loading="lazy" decoding="async"' if lazy else ""
    srcset = copias(rel, w) if rel.endswith(".webp") and rel.startswith("assets/img/") else ""
    s = f' srcset="{srcset}" sizes="{sizes}"' if srcset else ""
    return f'<img src="/{rel}"{s} alt="{e(alt)}" width="{w}" height="{h}"{a}{l}>'


def mailto(subject):
    return f"mailto:{EMAIL}?subject={e(subject)}"


def sentence(t):
    """'Materiales para Vulcanizar' -> 'Materiales para vulcanizar' (respeta siglas como PVC)."""
    t = t[0] + t[1:].lower()
    return t.replace("pvc", "PVC")


# ---------------------------------------------------------------- plantilla

def analitica():
    if not ANALITICA_TOKEN:
        return ""
    return (
        "\n  <!-- Cloudflare Web Analytics (sin cookies) -->"
        '\n  <script type="module" src="https://static.cloudflareinsights.com/beacon.min.js" '
        f"data-cf-beacon='{{\"token\": \"{ANALITICA_TOKEN}\"}}'></script>"
    )


def head(title, desc, og_img=None, lang="es", path="/"):
    full = f"{title} | CRM Componentes" if title else "CRM Componentes — Comercial de Recambios Montemayor"
    idiomas = ""
    if path in PAGINA_IDIOMA:
        clave = PAGINA_IDIOMA[path]
        idiomas = "".join(f'\n  <link rel="alternate" hreflang="{l}" href="{SITE}{I.RUTAS[l][clave]}">' for l in I.IDIOMAS)
        idiomas += f'\n  <link rel="alternate" hreflang="x-default" href="{SITE}{I.RUTAS["es"][clave]}">'
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(full)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="theme-color" content="#ffffff">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="{"es_ES" if lang == "es" else I.T[lang]["locale"]}">
  <meta property="og:site_name" content="CRM Componentes">
  <meta property="og:title" content="{e(full)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:image" content="{SITE}/{og_img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">{idiomas}
  <link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/css/base.css?v={VERSION}">
  <link rel="stylesheet" href="/assets/css/layout.css?v={VERSION}">
  <link rel="stylesheet" href="/assets/css/components.css?v={VERSION}">
  <script src="/assets/js/main.js?v={VERSION}" defer></script>{analitica()}
</head>"""


NAV = [
    ("/", "Inicio", "inicio"),
    ("/productos/", "Productos", "productos"),
    ("/sectores/", "Sectores", "sectores"),
    ("/catalogos/", "Catálogos", "catalogos"),
    ("/quienes-somos/", "Quiénes somos", "quienes-somos"),
    ("/noticias/", "Noticias", "noticias"),
    ("/contacto/", "Contacto", "contacto"),
]


CHEVRON = '<svg class="icon nav__chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>'
MEGA_ORDER = ["elevacion", "bandas-transportadoras", "faldetas", "bandas-pvc"]


def mega_menu(active):
    """Panel de Productos: en escritorio se despliega bajo la barra; en móvil son
    niveles que se deslizan (Menú › Productos › Categoría)."""
    cols = []
    for s in MEGA_ORDER:
        fams = "".join(
            f'<li><a href="/productos/{s}/#{x["slug"]}">{sentence(x["title"])}</a></li>'
            for x in C["products"][s]
        )
        cur = ' aria-current="page"' if active == f"productos/{s}" else ""
        cols.append(f"""
              <div class="mega__col">
                <a class="mega__cat" href="/productos/{s}/" data-drill="sub-{s}"{cur}>{badge(CAT_ICON[s], "sm")}<span>{NAMES[s]}</span>{CHEVRON}</a>
                <div class="mega__sub" id="sub-{s}">
                  <button class="drill-back" type="button" data-drill-back>‹ Productos</button>
                  <p class="drill-title">{NAMES[s]}</p>
                  <a class="drill-all" href="/productos/{s}/">Ver todo {NAMES[s]}</a>
                  <ul class="mega__list">{fams}</ul>
                </div>
              </div>""")
    return f"""
            <div class="mega" id="mega-productos">
              <div class="mega__inner">
                <button class="drill-back" type="button" data-drill-back>‹ Menú</button>
                <p class="drill-title">Productos</p>
                <div class="mega__grid">{"".join(cols)}
                </div>
                <div class="mega__foot">
                  <a class="more" href="/productos/">Ver todos los productos</a>
                  <a class="more" href="/catalogos/">Pedir un catálogo</a>
                  <a class="more" href="tel:{PHONE_TEL}">Llamar al {PHONE}</a>
                  <a class="more" href="{wa("Hola, quería información sobre vuestros productos.")}" target="_blank" rel="noopener">WhatsApp</a>
                </div>
              </div>
            </div>"""


BANDERA = {  # banderas simplificadas en SVG (los emojis de bandera no se ven en Windows)
    "es": '<rect width="30" height="20" fill="#AA151B"/><rect y="5" width="30" height="10" fill="#F1BF00"/>',
    "en": ('<rect width="30" height="20" fill="#012169"/>'
           '<path d="M0 0 30 20M30 0 0 20" stroke="#fff" stroke-width="4"/>'
           '<path d="M0 0 30 20M30 0 0 20" stroke="#C8102E" stroke-width="1.6"/>'
           '<path d="M15 0v20M0 10h30" stroke="#fff" stroke-width="6.5"/>'
           '<path d="M15 0v20M0 10h30" stroke="#C8102E" stroke-width="3.6"/>'),
    "fr": '<rect width="10" height="20" fill="#002654"/><rect x="10" width="10" height="20" fill="#fff"/><rect x="20" width="10" height="20" fill="#CE1126"/>',
    "de": '<rect width="30" height="20" fill="#000"/><rect y="6.67" width="30" height="6.66" fill="#DD0000"/><rect y="13.33" width="30" height="6.67" fill="#FFCE00"/>',
}


def bandera(lang):
    return f'<svg class="flag" viewBox="0 0 30 20" aria-hidden="true">{BANDERA[lang]}</svg>'


def selector_idioma(path, lang):
    """Banderas para cambiar de idioma. Llevan a la misma página en el otro idioma si existe;
    si no, a la portada de ese idioma."""
    clave = PAGINA_IDIOMA.get(path, "inicio")
    enlaces = []
    for l in I.IDIOMAS:
        actual = ' aria-current="true"' if l == lang else ""
        enlaces.append(f'<a class="lang" href="{I.RUTAS[l][clave]}" hreflang="{l}" lang="{l}" title="{I.NOMBRE_IDIOMA[l]}"{actual}>'
                       f'{bandera(l)}<span class="lang__name">{I.NOMBRE_IDIOMA[l]}</span></a>')
    aria = "Idioma" if lang == "es" else I.T[lang]["idioma"]
    return f'<li class="nav__langs" role="group" aria-label="{aria}">{"".join(enlaces)}</li>'


def header_int(lang, active, path):
    """Cabecera de las versiones en otros idiomas (inglés, francés, alemán)."""
    t, rutas = I.T[lang], I.RUTAS[lang]
    items = "".join(
        f'<li><a class="nav__link" href="{rutas[k]}"{" aria-current=\"page\"" if f"{lang}-{k}" == active else ""}>{t["nav"][k]}</a></li>'
        for k in ("inicio", "productos", "empresa", "contacto")
    ) + selector_idioma(path, lang)
    return f"""<body>
  <a class="skip-link" href="#contenido">{t["saltar"]}</a>

  <header class="site-header">
    <div class="container">
      <a class="brand" href="{rutas["inicio"]}" aria-label="{t["inicio_aria"]}">
        <img src="/assets/img/brand/logo-crm.png" alt="CRM" width="500" height="173">
      </a>
      <nav class="nav" id="menu" aria-label="{t["menu_aria"]}">
        <ul class="nav__list">
          {items}
        </ul>
        <div class="nav__extra">
          {t["atencion"]}
          <a href="tel:{PHONE_TEL}">{PHONE}</a>
          <a href="{wa(t["wa"])}" target="_blank" rel="noopener">WhatsApp +34 {WHATSAPP_VER}</a>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
        </div>
      </nav>
      <a class="header-call" href="tel:{PHONE_TEL}">{icon("phone")} {t["llamar"]}</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="menu" aria-label="{t["abrir_menu"]}">
        <span class="nav-toggle__icon" aria-hidden="true"><span></span><span></span><span></span></span>
        <span class="nav-toggle__label" aria-hidden="true"></span>
      </button>
    </div>
  </header>
  <div class="nav-scrim" aria-hidden="true"></div>
"""


def header(active, path="/"):
    items = []
    for href, label, key in NAV:
        if key == "productos":
            cur = ' aria-current="page"' if active == "productos" else ""
            cls = "nav__link nav__link--mega is-current" if active.startswith("productos") else "nav__link nav__link--mega"
            items.append(
                f'<li class="nav__item--mega"><a class="{cls}" href="{href}" data-drill="mega-productos" '
                f'aria-haspopup="true" aria-expanded="false" aria-controls="mega-productos"{cur}>{label}{CHEVRON}</a>{mega_menu(active)}\n          </li>'
            )
        elif key == active:
            items.append(f'<li><a class="nav__link" href="{href}" aria-current="page">{label}</a></li>')
        else:
            items.append(f'<li><a class="nav__link" href="{href}">{label}</a></li>')
    items.append(selector_idioma(path, "es"))
    return f"""<body>
  <a class="skip-link" href="#contenido">Saltar al contenido</a>

  <header class="site-header">
    <div class="container">
      <a class="brand" href="/" aria-label="CRM Componentes — Inicio">
        <img src="/assets/img/brand/logo-crm.png" alt="CRM" width="500" height="173">
      </a>
      <nav class="nav" id="menu" aria-label="Principal">
        <ul class="nav__list">
          {"".join(items)}
        </ul>
        <div class="nav__extra">
          Atención al cliente
          <a href="tel:{PHONE_TEL}">{PHONE}</a>
          <a href="{wa()}" target="_blank" rel="noopener">WhatsApp {WHATSAPP_VER}</a>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
        </div>
      </nav>
      <a class="header-call" href="tel:{PHONE_TEL}">{icon("phone")} Llamar</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="menu" aria-label="Abrir menú">
        <span class="nav-toggle__icon" aria-hidden="true"><span></span><span></span><span></span></span>
        <span class="nav-toggle__label" aria-hidden="true"></span>
      </button>
    </div>
  </header>
  <div class="nav-scrim" aria-hidden="true"></div>
"""


FOOTER = f"""
  <footer class="site-footer">
    <div class="container">
      <p class="footer__lead">¿Necesitas ayuda? Llámanos al <a href="tel:{PHONE_TEL}"><strong>{PHONE}</strong></a>, escríbenos por <a href="{wa()}" target="_blank" rel="noopener"><strong>WhatsApp</strong></a> o a <a href="mailto:{EMAIL}"><strong>{EMAIL}</strong></a>.</p>
      <div class="footer__grid">
        <div>
          <h2>Productos</h2>
          <ul class="footer__links">
            {"".join(f'<li><a href="/productos/{s}/">{n}</a></li>' for s, n, _ in PRODUCTS)}
          </ul>
        </div>
        <div>
          <h2>Sectores</h2>
          <ul class="footer__links">
            {"".join(f'<li><a href="/sectores/{x["slug"]}/">{x["nombre"]}</a></li>' for x in SECTORES)}
          </ul>
        </div>
        <div>
          <h2>Empresa</h2>
          <ul class="footer__links">
            <li><a href="/quienes-somos/">Quiénes somos</a></li>
            <li><a href="/catalogos/">Catálogos</a></li>
            <li><a href="/noticias/">Noticias</a></li>
            <li><a href="/contacto/">Contacto</a></li>
          </ul>
        </div>
        <div>
          <h2>Legal</h2>
          <ul class="footer__links">
            <li><a href="/legal/aviso-legal/">Aviso legal</a></li>
            <li><a href="/legal/politica-de-privacidad/">Privacidad</a></li>
            <li><a href="/legal/politica-de-cookies/">Cookies</a></li>
            <li><a href="/legal/politica-de-redes-sociales/">Redes sociales</a></li>
          </ul>
        </div>
        <div>
          <h2>Visítanos</h2>
          <p style="margin:0">P.I. Los Alfares<br>Calle La Jarra 41<br>14540 La Rambla (Córdoba)</p>
        </div>
      </div>
      <div class="footer__bottom">
        <span>© <span data-year>2026</span> Comercial de Recambios Montemayor, S.L.</span>
        <span>CIF B14392799</span>
      </div>
    </div>
  </footer>

  <nav class="callbar" aria-label="Contacto rápido">
    <a href="tel:{PHONE_TEL}">{icon("phone")} Llamar</a>
    <a class="callbar__wa" href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")} WhatsApp</a>
    <a href="mailto:{EMAIL}">{icon("mail")} Email</a>
  </nav>
</body>
</html>
"""


def nombre_cat(lang, slug):
    if lang == "es":
        return NAMES[slug]
    return NAMES_EN[slug] if lang == "en" else I.CATEGORIAS[lang][slug][0]


def corto_cat(lang, slug):
    if lang == "es":
        return SHORT[slug]
    return SHORT_EN[slug] if lang == "en" else I.CATEGORIAS[lang][slug][1]


def nombre_fam(lang, cat, f):
    return f["nombre_en"] if lang == "en" else I.FAMILIAS[lang][f"{cat}/{f['slug']}"]


def footer_int(lang):
    """Pie de las versiones en otros idiomas."""
    t, rutas = I.T[lang], I.RUTAS[lang]
    wa_url = wa(t["wa"])
    ayuda = t["pie_ayuda"].format(
        tel=f'<a href="tel:{PHONE_TEL}"><strong>{PHONE}</strong></a>',
        wa=f'<a href="{wa_url}" target="_blank" rel="noopener"><strong>WhatsApp</strong></a>',
        mail=f'<a href="mailto:{EMAIL}"><strong>{EMAIL}</strong></a>')
    otros = "".join(f'<li><a href="{I.RUTAS[l]["inicio"]}" hreflang="{l}" lang="{l}">{I.NOMBRE_IDIOMA[l]}</a></li>'
                    for l in I.IDIOMAS if l != lang)
    return f"""
  <footer class="site-footer">
    <div class="container">
      <p class="footer__lead">{ayuda}</p>
      <div class="footer__grid">
        <div>
          <h2>{t["pie_productos"]}</h2>
          <ul class="footer__links">
            {"".join(f'<li><a href="{rutas["productos"]}#{s}">{nombre_cat(lang, s)}</a></li>' for s, _, _ in PRODUCTS)}
          </ul>
        </div>
        <div>
          <h2>{t["pie_empresa"]}</h2>
          <ul class="footer__links">
            <li><a href="{rutas["empresa"]}">{t["nav"]["empresa"]}</a></li>
            <li><a href="{rutas["contacto"]}">{t["nav"]["contacto"]}</a></li>
          </ul>
        </div>
        <div>
          <h2>{t["idioma"]}</h2>
          <ul class="footer__links">
            {otros}
          </ul>
        </div>
        <div>
          <h2>{t["pie_legal"]}</h2>
          <ul class="footer__links">
            <li><a href="/legal/aviso-legal/" hreflang="es">{t["aviso_legal"]}</a></li>
            <li><a href="/legal/politica-de-privacidad/" hreflang="es">{t["privacidad"]}</a></li>
          </ul>
        </div>
        <div>
          <h2>{t["pie_visita"]}</h2>
          <p style="margin:0">P.I. Los Alfares<br>Calle La Jarra 41<br>14540 La Rambla (Córdoba), {t["pais"]}</p>
        </div>
      </div>
      <div class="footer__bottom">
        <span>© <span data-year>2026</span> Comercial de Recambios Montemayor, S.L.</span>
        <span>{t["cif"]}</span>
      </div>
    </div>
  </footer>

  <nav class="callbar" aria-label="{t["contacto_rapido"]}">
    <a href="tel:{PHONE_TEL}">{icon("phone")} {t["llamar"]}</a>
    <a class="callbar__wa" href="{wa_url}" target="_blank" rel="noopener">{icon("whatsapp")} WhatsApp</a>
    <a href="mailto:{EMAIL}">{icon("mail")} Email</a>
  </nav>
</body>
</html>
"""



FRASE_COMPARTIR = "Componentes para elevación y transporte · La Rambla (Córdoba)"


def imagen_compartir(path, title, foto=None, frase=None):
    """Genera assets/img/compartir/<página>.jpg y devuelve su ruta."""
    nombre = path.strip("/").replace("/", "-") or "inicio"
    rel = f"assets/img/compartir/{nombre}.jpg"
    generar_imagen_compartir(os.path.join(REPO, rel), title or "CRM Componentes", frase or FRASE_COMPARTIR,
                             foto=os.path.join(REPO, foto) if foto else None,
                             logo=os.path.join(REPO, "assets", "img", "brand", "logo-crm.png"))
    return rel


def write(path, title, desc, active, body, og_img=None, og_titulo=None, og_frase=None, lang="es"):
    """og_img: foto de fondo para la imagen al compartir (si no, fondo verde)."""
    if path == "/404":
        compartir = "assets/img/compartir/inicio.jpg"
    else:
        if path != "/presupuesto/gracias/":   # la página de gracias no va al sitemap
            PAGINAS.append(path)
        compartir = imagen_compartir(path, og_titulo or title, og_img, og_frase)
    cabecera = header(active, path) if lang == "es" else header_int(lang, active, path)
    pie = FOOTER if lang == "es" else footer_int(lang)
    out = head(title, desc, compartir, lang, path) + "\n" + cabecera + '\n  <main id="contenido">' + body + "\n  </main>\n" + pie
    file = os.path.join(REPO, path.strip("/"), "index.html") if path != "/404" else os.path.join(REPO, "404.html")
    os.makedirs(os.path.dirname(file), exist_ok=True)
    open(file, "w", encoding="utf-8", newline="\n").write(out)
    print("ok", path)


def intro(h1, lead="", eyebrow="", actions="", icon_name=None):
    parts = []
    if icon_name:
        parts.append(badge(icon_name, "lg"))
    if eyebrow:
        parts.append(f'<span class="eyebrow">{eyebrow}</span>')
    parts.append(f"<h1>{h1}</h1>")
    if lead:
        parts.append(f'<p class="lead">{lead}</p>')
    if actions:
        parts.append(f'<div class="actions">{actions}</div>')
    inner = "\n        ".join(parts)
    return f"""
    <section class="page-intro">
      <div class="container">
        {inner}
      </div>
    </section>"""


def migas(*pasos):
    """Datos estructurados de la ruta de la página (Google la muestra en los resultados):
    migas(("Productos", "/productos/"), ("Elevación", "/productos/elevacion/"))."""
    datos = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": nombre, "item": SITE + ruta}
        for i, (nombre, ruta) in enumerate((("Inicio", "/"),) + pasos, 1)]}
    return f"""
    <script type="application/ld+json">{json.dumps(datos, ensure_ascii=False)}</script>"""


def cta():
    return f"""
    <section class="section section--tile center">
      <div class="container">
        {badge("handshake")}
        <h2 style="margin-top:28px">¿Hablamos?</h2>
        <p class="lead" style="max-width:600px;margin:0 auto 28px">Te ayudamos a elegir el producto adecuado para tu instalación.</p>
        <div class="actions">
          <a class="btn" href="tel:{PHONE_TEL}">{icon("phone")} {PHONE}</a>
          <a class="btn btn--wa" href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")} WhatsApp</a>
          <a class="more" href="/presupuesto/">Pedir presupuesto</a>
        </div>
      </div>
    </section>""".replace('<span class="badge-icon">', '<span class="badge-icon" style="margin:0 auto">', 1)


CAT_FOTO = {  # foto representativa que aparece al pasar el ratón por la tarjeta
    "elevacion": "assets/img/categorias/elevacion.webp",
    "bandas-transportadoras": "assets/img/categorias/bandas-transportadoras.webp",
    "faldetas": "assets/img/productos/faldetas/faldetas/01.webp",
    "bandas-pvc": "assets/img/productos/bandas-pvc/bandas-de-pvc/13.webp",
}


def catcard_head(s, titulo, texto, href):
    """Cabecera de la tarjeta: icono, nombre y frase, con la foto de la categoría detrás."""
    foto = img(CAT_FOTO[s], "", "catcard__photo", sizes="(max-width: 560px) 100vw, (max-width: 1000px) 50vw, 300px") if s in CAT_FOTO else ""
    return f"""<div class="catcard__head">{foto}
              {badge(CAT_ICON[s], "sm")}
              <h3><a href="{href}">{titulo}</a></h3>
              <p>{texto}</p>
            </div>"""


def product_tiles():
    """Tarjetas compactas e iguales de las 4 categorías, con sus familias visibles."""
    order = ["elevacion", "bandas-transportadoras", "faldetas", "bandas-pvc"]
    out = []
    for s in order:
        secs = C["products"][s]
        shown, rest = secs[:5], len(secs) - 5
        fams = "".join(f'<li><a href="/productos/{s}/#{x["slug"]}">{sentence(x["title"])}</a></li>' for x in shown)
        if rest > 0:
            fams += f'<li><a class="catcard__rest" href="/productos/{s}/#gama">y {rest} más</a></li>'
        out.append(f"""
          <article class="catcard">
            {catcard_head(s, NAMES[s], SHORT[s], f"/productos/{s}/")}
            <ul class="catcard__list">{fams}</ul>
            <a class="more" href="/productos/{s}/">Ver todo</a>
          </article>""")
    return '<div class="catcards">' + "".join(out) + "\n        </div>"


def news_cards(noticias):
    """Tarjetas de noticia con foto de portada, fecha, título y resumen."""
    out = []
    for n in noticias:
        foto = (f'<a class="newscard__media" href="/noticias/{n["slug"]}/" tabindex="-1" aria-hidden="true">'
                f'{img(n["fotos"][0], n["titulo"], sizes="(max-width: 700px) 100vw, 400px")}</a>') if n["fotos"] else ""
        out.append(f"""
          <article class="newscard">{foto}
            <div class="newscard__body">
              <time class="card__meta" datetime="{n["fecha"]}">{n["fecha_larga"]}</time>
              <h3><a href="/noticias/{n["slug"]}/">{e(n["titulo"])}</a></h3>
              <p>{e(n["resumen"])}</p>
              <a class="more" href="/noticias/{n["slug"]}/">Leer noticia</a>
            </div>
          </article>""")
    return '<div class="newscards">' + "".join(out) + "\n        </div>"


def ultimas_noticias():
    if not NOTICIAS:
        return ""
    return f"""
    <section class="section">
      <div class="container container--wide">
        <div class="headline">
          <h2>Últimas noticias.</h2>
          <p class="lead"><a class="more" href="/noticias/">Ver todas</a></p>
        </div>
        {news_cards(NOTICIAS[:3])}
      </div>
    </section>"""


def video_band(video, eyebrow, title, text, actions):
    """Franja con vídeo de fondo (sin sonido, en bucle). El JS solo lo carga si
    el usuario no pide reducir animaciones ni ahorrar datos; si no, queda la foto fija."""
    return f"""
    <section class="video-band">
      <video class="video-band__media" data-bg-video muted loop playsinline preload="none" poster="/assets/video/{video}.webp" aria-hidden="true">
        <source data-src="/assets/video/{video}.mp4" type="video/mp4">
      </video>
      <div class="container video-band__content">
        <span class="eyebrow">{eyebrow}</span>
        <h2>{title}</h2>
        <p class="lead">{text}</p>
        <div class="actions">{actions}</div>
      </div>
    </section>"""


SECTOR = {x["slug"]: x for x in SECTORES}


def sector_media(x, sizes):
    """Foto del sector o, si aún no hay foto, su icono sobre fondo verde."""
    if x.get("foto"):
        return img(x["foto"], "", sizes=sizes)
    return f'<span class="sector__nofoto">{icon(x["icono"])}</span>'


def sectores(lang="es"):
    """Franja de sectores con foto: cada uno lleva a su página de sector."""
    tarjetas = []
    for x in SECTORES:
        if lang == "es":
            nombre, href, sub = x["nombre"], f"/sectores/{x['slug']}/", "Ver productos"
        else:
            nombre, href, sub = I.SECTORES[lang][x["slug"]], I.RUTAS[lang]["productos"], I.T[lang]["ver_productos"]
        tarjetas.append(f"""
          <a class="sector" href="{href}">{sector_media(x, "(max-width: 900px) 50vw, 240px")}
            <span class="sector__text"><strong>{nombre}</strong><span>{sub}</span></span>
          </a>""")
    titulo, lead = (("Para tu sector.", "Del campo a la industria: soluciones para cada tipo de instalación.") if lang == "es"
                    else (I.T[lang]["sectores_h2"], I.T[lang]["sectores_lead"]))
    return f"""
    <section class="section section--flush-top">
      <div class="container container--wide">
        <div class="headline">
          <h2>{titulo}</h2>
          <p class="lead">{lead}</p>
        </div>
        <div class="sectors">{"".join(tarjetas)}
        </div>
      </div>
    </section>"""


def campana_vigente(hoy=None):
    """Campaña que toca en una fecha: la última que ha empezado (el ciclo da la vuelta al año)."""
    import datetime
    hoy = (hoy or datetime.date.today()).strftime("%m-%d")
    campanas = sorted((x["campana"]["desde"], x["slug"]) for x in SECTORES if x.get("campana"))
    empezadas = [c for c in campanas if c[0] <= hoy]
    return (empezadas or campanas)[-1][1]


def campanas():
    """Avisos de temporada de la portada. Se generan todos; el navegador deja visible el que toca
    según la fecha (main.js), así la portada cambia sola aunque no se vuelva a publicar."""
    vigente = campana_vigente()
    out = []
    for x in SECTORES:
        c = x.get("campana")
        if not c:
            continue
        foto = x.get("foto_grande") or x.get("foto")
        media = (img(foto, "", lazy=False, sizes="(max-width: 800px) 100vw, 560px") if foto
                 else f'<span class="season__nofoto">{icon(x["icono"])}</span>')
        oculta = "" if x["slug"] == vigente else " hidden"
        out.append(f"""
      <div class="season" data-campana="{c["desde"]}"{oculta}>
        <div class="season__text">
          <span class="eyebrow">{icon(x["icono"])} {c["nombre"]}</span>
          <h2>{c["titulo"]}</h2>
          <p>{c["texto"]}</p>
          <div class="actions actions--start">
            <a class="btn btn--wa" href="{wa(c["whatsapp"])}" target="_blank" rel="noopener">{icon("whatsapp")} Pedir por WhatsApp</a>
            <a class="more" href="/sectores/{x["slug"]}/">Productos para {x["nombre"].lower()}</a>
          </div>
        </div>
        <div class="season__media">{media}</div>
      </div>""")
    return f"""
    <section class="section section--tight" aria-label="Campaña de temporada">
      <div class="container container--wide">{"".join(out)}
      </div>
    </section>"""


# ---------------------------------------------------------------- inicio

jsonld = json.dumps({
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "Comercial de Recambios Montemayor, S.L. (CRM)",
    "url": SITE,
    "logo": SITE + "/assets/img/brand/logo-crm.png",
    "telephone": PHONE_TEL,
    "email": EMAIL,
    "foundingDate": "1994",
    "address": {"@type": "PostalAddress", "streetAddress": "P.I. Los Alfares, Calle La Jarra 41", "postalCode": "14540",
                "addressLocality": "La Rambla", "addressRegion": "Córdoba", "addressCountry": "ES"},
}, ensure_ascii=False)

strip = "".join(
    f'<li><a href="/productos/{s}/">{badge(CAT_ICON[s])}<span>{NAMES[s]}</span></a></li>'
    for s in ["elevacion", "bandas-transportadoras", "faldetas", "bandas-pvc"]
)
body = f"""
    <section class="hero hero--photo" style="--hero-img:url('/assets/img/fondos/campo.webp')">
      <div class="container">
        <span class="eyebrow">Desde 1994 · La Rambla, Córdoba</span>
        <h1>Soluciones y <span class="gradient">máxima eficiencia.</span></h1>
        <p class="lead">Componentes para elevación y transporte de materiales, con stock permanente y fabricación a medida.</p>
        <div class="actions">
          <a class="btn" href="/productos/">Ver productos</a>
          <a class="more" href="tel:{PHONE_TEL}">Llamar al {PHONE}</a>
        </div>
      </div>
    </section>
{campanas()}


    <section class="section">
      <div class="container container--wide">
        <div class="headline">
          <h2>Nuestros productos.</h2>
          <p class="lead">Todo lo que tu instalación necesita, en un solo proveedor.</p>
        </div>
        {product_tiles()}
      </div>
    </section>
{sectores()}
{video_band("corte-fieltro", "Fabricación a medida", "Lo cortamos a tu medida.",
            "Fieltro, goma y caramelo cortados y perforados en nuestras instalaciones de La Rambla.",
            '<a class="btn btn--light" href="/productos/faldetas/">Componentes para vibradores</a><a class="more" href="/quienes-somos/#instalaciones">Nuestras instalaciones</a>')}

    <section class="section section--tight section--tile">
      <div class="container container--wide">
        <ul class="facts">
          <li>{icon("calendar")}<strong>Desde 1994</strong><span>Empresa familiar</span></li>
          <li>{icon("box")}<strong>Stock permanente</strong><span>Entrega inmediata</span></li>
          <li>{icon("ruler")}<strong>A medida</strong><span>Corte, perforado y piezas</span></li>
          <li>{icon("award")}<strong>Primeras marcas</strong><span>Europeas y españolas</span></li>
        </ul>
      </div>
    </section>

{ultimas_noticias()}
    <section class="section section--dark">
      <div class="container center">
        <p class="statement">Calidad antes que cantidad. <span>Preferimos tener buenos clientes y darles un servicio personalizado. Por eso cada día son más los que confían en nosotros.</span></p>
        <div class="actions" style="margin-top:32px"><a class="more" href="/quienes-somos/">Conócenos</a></div>
      </div>
    </section>
{cta()}
    <script type="application/ld+json">{jsonld}</script>"""
write("/", None, "CRM — Comercial de Recambios Montemayor (La Rambla, Córdoba). Bandas transportadoras, bandas de PVC, faldetas y componentes para elevación. Stock permanente desde 1994.", "inicio", body,
      og_img="assets/img/fondos/campo.webp", og_titulo="Soluciones y máxima eficiencia.",
      og_frase="CRM · Componentes para elevación y transporte desde 1994")

# ---------------------------------------------------------------- productos (índice)

body = intro("Productos.", "Componentes para elevación, transporte por banda y fabricación a medida en goma, fieltro y PVC.")
body += f"""
    <section class="section section--flush-top">
      <div class="container container--wide">
        {product_tiles()}
      </div>
    </section>""" + cta()
write("/productos/", "Productos", "Productos de CRM: elevación, bandas transportadoras, faldetas y bandas de PVC.", "productos", body)

# ---------------------------------------------------------------- páginas de producto

def section_photos(slug, s):
    """Fotos de una familia: assets/img/productos/<categoria>/<familia>/*.webp (orden alfabético)."""
    folder = os.path.join(REPO, "assets", "img", "productos", slug, s["slug"])
    if not os.path.isdir(folder):
        return []
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
    return [f"assets/img/productos/{slug}/{s['slug']}/{f}" for f in files]


def carousel_html(name, pics, label):
    """pics: lista de (ruta, texto alternativo). No genera nada si no hay fotos."""
    if not pics:
        return ""
    slides = "".join(
        f'<a class="carousel__slide" href="/{r}" data-gallery="{name}" data-alt="{e(alt)}" '
        f'aria-label="Ampliar foto {i} de {len(pics)}">{img(r, alt)}</a>'
        for i, (r, alt) in enumerate(pics, 1)
    )
    controls = ""
    if len(pics) > 1:
        controls = """
              <div class="carousel__controls">
                <button class="carousel__btn" type="button" data-carousel-prev aria-label="Foto anterior">‹</button>
                <div class="carousel__dots" aria-hidden="true"></div>
                <button class="carousel__btn" type="button" data-carousel-next aria-label="Foto siguiente">›</button>
              </div>"""
    return f"""
            <div class="carousel" data-carousel aria-roledescription="carrusel" aria-label="{e(label)}">
              <div class="carousel__track">{slides}</div>{controls}
            </div>"""


def carousel(slug, s):
    pics = [(r, f"{s['title']} — foto {i}") for i, r in enumerate(section_photos(slug, s), 1)]
    return carousel_html(f"{slug}-{s['slug']}", pics, f"Fotos de {s['title']}")


def product_page(slug, name, intro_text):
    secs = [dict(x, title=sentence(x["title"])) for x in C["products"][slug]]
    body = f"""
    <nav class="localnav" aria-label="{e(name)}">
      <div class="container">
        <a class="localnav__title" href="#contenido">{name}</a>
        <a class="localnav__link" href="#gama">Gama</a>
        <a class="btn" href="{presupuesto(name)}">Presupuesto</a>
      </div>
    </nav>"""
    body += intro(
        f"{name}.",
        intro_text,
        eyebrow='<a href="/productos/">Productos</a>',
        actions=f'<a class="btn" href="{presupuesto(name)}">Pedir presupuesto</a><a class="more" href="{wa("Hola, quería información sobre " + name.lower() + ".")}" target="_blank" rel="noopener">WhatsApp</a><a class="more" href="tel:{PHONE_TEL}">Llamar</a>',
        icon_name=CAT_ICON[slug],
    )
    rng = "".join(f'<a href="#{s["slug"]}">{icon(SEC_ICON[slug][s["slug"]])}<span>{s["title"]}</span></a>' for s in secs)
    body += f"""

    <section class="section section--tight section--tile" id="gama">
      <div class="container container--wide">
        <div class="headline">
          <h2>Explora la gama.</h2>
          <p class="lead">Toca una familia para ver su información.</p>
        </div>
        <div class="range">{rng}</div>
      </div>
    </section>

    <section class="section">
      <div class="container container--wide products-list">"""
    for i, s in enumerate(secs, 1):
        text = TEXT.get(slug, {}).get(s["slug"]) or "\n<p>Consúltanos medidas, calidades y disponibilidad.</p>"
        extra = EXTRA.get((slug, s["slug"]), "")
        open_attr = " open" if i == 1 else ""
        body += f"""
        <details class="product" id="{s["slug"]}"{open_attr}>
          <summary class="product__summary">
            <div class="product__head">
              {icon(SEC_ICON[slug][s["slug"]])}
              <h2>{s["title"]}</h2>
              <span class="product__toggle" aria-hidden="true"></span>
            </div>
          </summary>
          <div class="product__body">
            <div class="product__text">{text}
            </div>{carousel(slug, s)}{extra}
            <div class="product__actions">
              <a class="btn btn--wa" href="{wa("Hola, quería información sobre " + s["title"].lower() + " (" + name + ").")}" target="_blank" rel="noopener">{icon("whatsapp")} Preguntar por WhatsApp</a>
              <a class="btn btn--outline" href="{presupuesto(name + " · " + s["title"])}">Pedir presupuesto</a>
            </div>
          </div>
        </details>"""
    body += """
      </div>
    </section>""" + cta() + migas(("Productos", "/productos/"), (name, f"/productos/{slug}/"))
    names = ", ".join(s["title"].lower() for s in secs)
    fotos_cat = [p for sec in secs for p in section_photos(slug, sec)]
    write(f"/productos/{slug}/", name, f"{name} en CRM (La Rambla, Córdoba): {names}.", f"productos/{slug}", body,
          og_img=fotos_cat[0] if fotos_cat else None, og_frase=SHORT[slug])


for slug, name, intro_text in PRODUCTS:
    product_page(slug, name, intro_text)

# ---------------------------------------------------------------- sectores

FAMILIA = {(c["slug"], f["slug"]): f for c in CATEGORIAS for f in c["familias"]}   # solo las visibles


def tarjetas_producto(pares):
    """Tarjetas de las familias de producto de un sector, con su primera foto o su icono."""
    out = []
    for cat, fam in pares:
        f = FAMILIA.get((cat, fam))
        if not f:          # familia oculta o inexistente
            continue
        fotos = section_photos(cat, {"slug": fam})
        media = (img(fotos[0], "", sizes="(max-width: 560px) 50vw, 280px") if fotos
                 else f'<span class="prodcard__icon">{icon(f["icono"])}</span>')
        out.append(f"""
          <a class="prodcard" href="/productos/{cat}/#{fam}">
            <span class="prodcard__media">{media}</span>
            <span class="prodcard__text"><strong>{e(sentence(f["nombre"]))}</strong><span>{e(NAMES[cat])}</span></span>
          </a>""")
    return '<div class="prodcards">' + "".join(out) + "\n        </div>"


for x in SECTORES:
    ruta = f"/sectores/{x['slug']}/"
    nombre_min = x["nombre"].lower()
    body = intro(
        x["titulo"] + ".",
        x["intro"],
        eyebrow='<a href="/sectores/">Sectores</a> · ' + x["nombre"],
        actions=(f'<a class="btn btn--wa" href="{wa("Hola, quería información de productos para " + nombre_min + ".")}" target="_blank" rel="noopener">{icon("whatsapp")} WhatsApp</a>'
                 f'<a class="more" href="{presupuesto(x["nombre"])}">Pedir presupuesto</a><a class="more" href="tel:{PHONE_TEL}">Llamar</a>'),
        icon_name=x["icono"],
    )
    foto = x.get("foto_grande") or x.get("foto")
    if foto:
        body += f"""
    <div class="container container--wide page-photo">{img(foto, x["nombre"], lazy=False)}</div>"""
    body += f"""
    <section class="section">
      <div class="container prose">{x["texto"]}
      </div>
    </section>

    <section class="section section--tile">
      <div class="container container--wide">
        <div class="headline">
          <h2>Productos para {nombre_min}.</h2>
          <p class="lead">Toca un producto para ver medidas, calidades y fotos.</p>
        </div>
        {tarjetas_producto(x["productos"])}
      </div>
    </section>""" + cta() + migas(("Sectores", "/sectores/"), (x["nombre"], ruta))
    write(ruta, x["titulo"], x["descripcion"], "sectores", body, og_img=foto, og_titulo=x["titulo"],
          og_frase=f"CRM · {x['nombre']}")

body = intro("Sectores.", "Del olivar a la cantera: elige tu sector y te enseñamos los productos que necesitas.")
body += sectores().replace('section--flush-top">', 'section--flush-top" id="lista">', 1).replace(
    '<div class="headline">\n          <h2>Para tu sector.</h2>\n          <p class="lead">Del campo a la industria: soluciones para cada tipo de instalación.</p>\n        </div>\n        ', "")
body += cta() + migas(("Sectores", "/sectores/"),)
write("/sectores/", "Sectores", "Productos de CRM por sector: olivar, almendro, ajo, cereal y silos, e industria, canteras y reciclaje.", "sectores", body)

# ---------------------------------------------------------------- quiénes somos

body = intro("Una empresa familiar <span class=\"gradient\">desde 1994.</span>", "Pasado, tecnología. Presente, innovación. Futuro, sostenible.",
             eyebrow="Quiénes somos")
INSTALACIONES = [
    ("assets/img/empresa/oficinas.webp", "Oficinas de CRM en el P.I. Los Alfares"),
    ("assets/img/empresa/cnc-1.webp", "Máquina de corte por control numérico (CNC)"),
    ("assets/img/empresa/corte-cnc-goma.webp", "Corte de goma en la CNC"),
    ("assets/img/empresa/cnc-2.webp", "Cabezal de corte de la CNC"),
    ("assets/img/empresa/alta-frecuencia-1.webp", "Máquina de alta frecuencia para bandas de PVC"),
    ("assets/img/empresa/alta-frecuencia-2.webp", "Soldadura de perfiles en bandas de PVC"),
    ("assets/img/empresa/planchas-2.webp", "Planchas de goma y fieltro en stock"),
    ("assets/img/empresa/fachada.webp", "Fachada de la nueva nave"),
    ("assets/img/empresa/nave-nueva-1.webp", "Nueva nave en construcción"),
    ("assets/img/empresa/nave-nueva-2.webp", "Estructura de la nueva nave"),
]
body += f"""

    <div class="container container--wide page-photo">{img("assets/img/empresa/oficinas.webp", "Oficinas de CRM en el P.I. Los Alfares, La Rambla", lazy=False)}</div>

    <section class="section section--flush-top">
      <div class="container">
        <ul class="values">
          <li>{badge("wrench", "sm")}<h3>Profesionales</h3><p>Somos una empresa dedicada a profesionales, con una gran experiencia en todos nuestros productos.</p></li>
          <li>{badge("award", "sm")}<h3>Primeras marcas</h3><p>Contamos con el apoyo de fabricantes europeos que no tenían presencia en España y de primeras marcas españolas.</p></li>
          <li>{badge("refresh", "sm")}<h3>Gama siempre al día</h3><p>Recogemos la experiencia de nuestros clientes y actualizamos constantemente nuestros productos.</p></li>
          <li>{badge("truck", "sm")}<h3>Bien comunicados</h3><p>A 20 minutos de Córdoba, a una hora de Sevilla, Málaga, Granada y Jaén, y a 2 horas de Cádiz, Huelva y Ciudad Real.</p></li>
        </ul>
      </div>
    </section>

    <section class="section section--flush-top">
      <div class="container container--wide identity">
        <div class="identity__text">
          <span class="eyebrow">Garantía de satisfacción</span>
          <h2>Nuestra seña de identidad.</h2>
          <p>En CRM creemos que es mejor tener buenos clientes y darles un servicio personalizado que tener muchos clientes y no atenderlos lo suficientemente bien. Por eso nos eligen: prefieren un servicio de calidad y no de cantidad.</p>
          <p>Si de algo estamos orgullosos es de que cada día somos más los que establecemos este vínculo. Gracias a todos los que confiáis en nosotros, desde la familia que formamos todos.</p>
        </div>
        <div class="identity__photo">{img("assets/img/empresa/planchas-1.webp", "Palés de planchas de goma y fieltro preparados en nuestra nave", sizes="(max-width: 800px) 100vw, 600px")}</div>
      </div>
    </section>

    <section class="section section--tile" id="instalaciones">
      <div class="container">
        <div class="headline">
          <h2>Nuestras instalaciones.</h2>
          <p class="lead">Maquinaria propia para cortar, perforar y fabricar a medida. Y una nueva nave en marcha.</p>
        </div>
        {carousel_html("instalaciones", INSTALACIONES, "Fotos de nuestras instalaciones")}
      </div>
    </section>
{video_band("corte-cnc", "Corte por control numérico", "Precisión en cada pieza.",
            "Cortamos goma y fieltro en nuestra máquina CNC, según plano o muestra.",
            f'<a class="btn btn--light" href="{mailto("Consulta: fabricación a medida")}">Pedir presupuesto</a>')}

    <section class="section">
      <div class="container container--wide">
        <div class="headline">
          <h2>Nuestra historia.</h2>
          <p class="lead">Una aventura familiar que empezó con un cambio radical en nuestras vidas.</p>
        </div>
        <ol class="years">
          <li>
            <span class="years__num gradient">1994</span>
            <h3>Fundamos CRM S.L.</h3>
            <p>Con la ilusión de hacer algo diferente y la experiencia de muchos años en el sector. Los primeros años fueron duros, pero con mucho sacrificio empezamos a crecer e invertir.</p>
          </li>
          <li>
            <span class="years__num gradient">1999</span>
            <h3>Nueva nave de 500 m².</h3>
            <p>Desde el año 2000 empezamos a tener clientes en todo el país, y en 2002 adquirimos una nueva parcela en el polígono.</p>
          </li>
          <li>
            <span class="years__num gradient">2005</span>
            <h3>Otros 500 m² más.</h3>
            <p>Ampliamos la nave para almacenar nuevos productos y albergar nuevas máquinas con las que ser más competitivos.</p>
          </li>
        </ol>
      </div>
    </section>

    <section class="section section--dark">
      <div class="container">
        <p class="statement">Hemos llegado hasta aquí gracias a la familia, clientes y proveedores. <span>Gracias.</span></p>
      </div>
    </section>
{cta()}"""
write("/quienes-somos/", "Quiénes somos", "CRM S.L. es una empresa familiar fundada en 1994 en La Rambla (Córdoba), especializada en componentes para elevación y transporte de materiales.", "quienes-somos", body, og_img="assets/img/empresa/oficinas.webp", og_titulo="Una empresa familiar desde 1994")

# ---------------------------------------------------------------- catálogos

CATS = [
    ("Acero, goma y plástico", "Componentes en acero, goma y plástico técnico.", "nut"),
    ("Elevación", "Bandas elevadoras, cangilones y accesorios.", "elevator"),
    ("Faldetas", "Goma, fieltro y caramelo para vibradores.", "skirt"),
    ("Estaciones", "Soportes y estaciones para rodillos.", "idler"),
    ("Vulcanizados", "Empalmes, reparaciones y materiales.", "press"),
    ("CRM", "Catálogo general de la empresa.", "doc"),
    ("Bandas PVC", "Bandas alimentarias e industriales.", "cleated"),
]
cards = "".join(f"""
          <article class="card">
            {badge(ic, "sm")}
            <span class="card__meta">Catálogo</span>
            <h3>{t}</h3>
            <p>{d}</p>
            <a class="more" href="{mailto("Solicitud de catálogo: " + t)}">Solicitar por email</a>
          </article>""" for t, d, ic in CATS)
body = intro("Catálogos.", "Pídenos el catálogo que necesites y te lo enviamos por email.")
body += f"""
    <section class="section section--flush-top">
      <div class="container container--wide">
        <div class="cards">{cards}
        </div>
      </div>
    </section>""" + cta()
write("/catalogos/", "Catálogos", "Catálogos de productos de CRM: elevación, faldetas, estaciones, vulcanizados, bandas de PVC y más.", "catalogos", body)

# ---------------------------------------------------------------- noticias

for n in NOTICIAS:
    volver = '<a class="more more--back" href="/noticias/">Todas las noticias</a>'
    body = intro(e(n["titulo"]), e(n["resumen"]), eyebrow=f'<time datetime="{n["fecha"]}">{n["fecha_larga"]}</time>')
    fotos = [(r, f'{n["titulo"]} — foto {i}') for i, r in enumerate(n["fotos"], 1)]
    body += f"""
    <section class="section section--flush-top">
      <div class="container container--narrow">
        {carousel_html("noticia-" + n["slug"], fotos, "Fotos de la noticia")}
        <article class="prose news-body">
{n["html"]}
        </article>
        <p>{volver}</p>
      </div>
    </section>""" + cta()
    write(f'/noticias/{n["slug"]}/', n["titulo"], n["resumen"] or n["titulo"], "noticias", body,
          og_img=n["fotos"][0] if n["fotos"] else None, og_frase=n["resumen"] or None)

archivo = "".join(
    f'<li><time datetime="{a["fecha"]}">{fecha_larga(a["fecha"])}</time><span>{e(a["titulo"])}</span></li>'
    for a in ARCHIVO_NOTICIAS
)
body = intro("Noticias.", "Ferias, novedades y momentos destacados de CRM.")
if NOTICIAS:
    body += f"""
    <section class="section section--flush-top">
      <div class="container container--wide">
        {news_cards(NOTICIAS)}
      </div>
    </section>"""
body += f"""
    <section class="section{" section--tile" if NOTICIAS else " section--flush-top"}">
      <div class="container container--narrow">
        <h2 class="archive__title">Archivo</h2>
        <ul class="archive">{archivo}</ul>
      </div>
    </section>"""
write("/noticias/", "Noticias", "Noticias de CRM: ferias, novedades de producto, instalaciones y aniversarios.", "noticias", body)

# ---------------------------------------------------------------- contacto

MAP = "https://www.google.com/maps?q=Calle+La+Jarra+41,+14540+La+Rambla,+C%C3%B3rdoba&output=embed"
DIR = "https://www.google.com/maps/dir/?api=1&destination=Calle+La+Jarra+41,+14540+La+Rambla,+C%C3%B3rdoba"
body = intro("Contacto.", "Llámanos, mándanos un WhatsApp o escríbenos y uno de nuestros profesionales te responderá lo antes posible.",
             eyebrow="Comercial de Recambios Montemayor S.L.")
body += f"""
    <section class="section section--flush-top">
      <div class="container container--wide">
        <div class="contact-tiles">
          <a class="contact-tile" href="tel:{PHONE_TEL}">{badge("phone")}<h3>Llámanos</h3><strong>{PHONE}</strong><span>En horario comercial</span></a>
          <a class="contact-tile" href="{wa()}" target="_blank" rel="noopener">{badge("whatsapp")}<h3>WhatsApp</h3><strong>{WHATSAPP_VER}</strong><span>Mándanos un mensaje o una foto</span></a>
          <a class="contact-tile" href="mailto:{EMAIL}">{badge("mail")}<h3>Escríbenos</h3><strong>{EMAIL}</strong><span>Te respondemos lo antes posible</span></a>
          <a class="contact-tile" href="{DIR}" target="_blank" rel="noopener">{badge("pin")}<h3>Visítanos</h3><strong>C/ La Jarra 41</strong><span>P.I. Los Alfares · 14540 La Rambla (Córdoba)</span></a>
        </div>
      </div>
    </section>

    <section class="section section--tile">
      <div class="container">
        <div class="headline">
          {badge("clock").replace('<span class="badge-icon">', '<span class="badge-icon" style="margin:0 auto 28px">')}
          <h2>Horario.</h2>
          <p class="lead">De lunes a viernes.</p>
        </div>
        <div class="hours">
          <div class="hours__card">
            <h3>Invierno</h3>
            <p>Lunes a viernes</p>
            <span class="hours__time">8:30 – 13:30</span>
            <span class="hours__time">16:00 – 19:00</span>
          </div>
          <div class="hours__card">
            <h3>Verano</h3>
            <p>Lunes a viernes</p>
            <span class="hours__time">8:00 – 15:00</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container container--wide">
        <div class="map" data-map-src="{MAP}" data-map-title="Ubicación de CRM en La Rambla">
          <div class="map__placeholder">
            {badge("pin")}
            <strong>P.I. Los Alfares · C/ La Jarra 41 · La Rambla (Córdoba)</strong>
            <button class="btn" type="button">Mostrar mapa</button>
            <p>Al cargar el mapa se conectará con Google Maps, que puede usar sus propias cookies.</p>
          </div>
        </div>
      </div>
    </section>"""
write("/contacto/", "Contacto", f"Contacta con CRM en La Rambla (Córdoba): teléfono {PHONE}, email {EMAIL}. Horario y ubicación.", "contacto", body,
      og_img="assets/img/empresa/oficinas.webp", og_frase=f"Teléfono {PHONE} · WhatsApp {WHATSAPP_VER}")

def opciones_producto():
    grupos = []
    for c in CATEGORIAS:
        ops = "".join(f'<option>{e(c["nombre"])} · {e(f["nombre"])}</option>' for f in c["familias"])
        grupos.append(f'<optgroup label="{e(c["nombre"])}"><option>{e(c["nombre"])}</option>{ops}</optgroup>')
    return '<option value="">Elige un producto (opcional)</option>' + "".join(grupos) + "<option>Otro / no lo sé</option>"


body = intro("Pide tu presupuesto.", "Cuéntanos qué necesitas y te contestamos lo antes posible. Si tienes una foto de la pieza, adjúntala: nos ayuda mucho.",
             eyebrow="Presupuesto sin compromiso")
body += f"""
    <section class="section section--flush-top">
      <div class="container container--narrow">
        <form class="quote" action="/api/presupuesto" method="post" enctype="multipart/form-data" data-quote novalidate>
          <div class="quote__grid">
            <label class="field">
              <span>Nombre <b aria-hidden="true">*</b></span>
              <input name="nombre" autocomplete="name" required>
            </label>
            <label class="field">
              <span>Empresa <small>(opcional)</small></span>
              <input name="empresa" autocomplete="organization">
            </label>
            <label class="field">
              <span>Teléfono <b aria-hidden="true">*</b></span>
              <input name="telefono" type="tel" inputmode="tel" autocomplete="tel" required>
            </label>
            <label class="field">
              <span>Email <small>(opcional)</small></span>
              <input name="email" type="email" autocomplete="email">
            </label>
            <label class="field">
              <span>Producto</span>
              <select name="producto" data-quote-producto>{opciones_producto()}</select>
            </label>
            <label class="field">
              <span>Cantidad <small>(opcional)</small></span>
              <input name="cantidad" placeholder="Ej.: 20 unidades, 50 metros…">
            </label>
            <label class="field field--wide">
              <span>Medidas o descripción</span>
              <textarea name="mensaje" rows="5" placeholder="Ancho, largo, espesor, calidad… o cuéntanos qué necesitas."></textarea>
            </label>
            <label class="field field--wide field--file">
              <span>{icon("camera")} Fotos de la pieza <small>(opcional, hasta 4)</small></span>
              <input name="fotos" type="file" accept="image/*" multiple data-quote-fotos>
            </label>
            <label class="field--check field--wide">
              <input type="checkbox" name="privacidad" value="si" required>
              <span>He leído y acepto la <a href="/legal/politica-de-privacidad/" target="_blank">política de privacidad</a>. <b aria-hidden="true">*</b></span>
            </label>
            <div class="field--trap" aria-hidden="true">
              <label>No rellenar <input name="web" tabindex="-1" autocomplete="off"></label>
            </div>
            <input type="hidden" name="t" value="">
          </div>
          <div class="quote__legal">
            <p class="quote__legal-title">Información básica sobre protección de datos</p>
            <dl>
              <dt>Responsable</dt><dd>Comercial de Recambios Montemayor, S.L.</dd>
              <dt>Finalidad</dt><dd>Atender tu solicitud y preparar el presupuesto.</dd>
              <dt>Legitimación</dt><dd>Tu consentimiento y la aplicación de medidas precontractuales a petición tuya.</dd>
              <dt>Destinatarios</dt><dd>No se ceden datos a terceros, salvo obligación legal. Cloudflare presta el alojamiento y el envío del formulario como encargado del tratamiento.</dd>
              <dt>Derechos</dt><dd>Acceso, rectificación, supresión, oposición, limitación y portabilidad, escribiendo a <a href="mailto:{EMAIL}">{EMAIL}</a>.</dd>
              <dt>Más información</dt><dd><a href="/legal/politica-de-privacidad/" target="_blank">Política de privacidad</a>.</dd>
            </dl>
          </div>
          <div class="quote__send">
            <button class="btn" type="submit">Enviar solicitud</button>
            <p class="quote__status" role="status" aria-live="polite"></p>
          </div>
        </form>
        <p class="quote__alt">¿Prefieres hablar? Llámanos al <a href="tel:{PHONE_TEL}">{PHONE}</a> o escríbenos por <a href="{wa()}" target="_blank" rel="noopener">WhatsApp</a>.</p>
      </div>
    </section>"""
write("/presupuesto/", "Pide tu presupuesto", "Pide presupuesto a CRM: bandas transportadoras, bandas de PVC, faldetas y componentes para elevación. Puedes adjuntar fotos.", "", body,
      og_titulo="Pide tu presupuesto", og_frase="Cuéntanos qué necesitas y adjunta una foto de la pieza")

body = intro("¡Gracias!", "Hemos recibido tu solicitud. Te contestaremos lo antes posible.", actions=f'<a class="btn" href="/productos/">Ver productos</a><a class="more" href="/">Ir al inicio</a>')
write("/presupuesto/gracias/", "Solicitud recibida", "Hemos recibido tu solicitud de presupuesto.", "", body)

# ---------------------------------------------------------------- legales

LEG = [
    ("aviso-legal", "Aviso legal"),
    ("politica-de-privacidad", "Política de privacidad"),
    ("politica-de-cookies", "Política de cookies"),
    ("politica-de-redes-sociales", "Política de redes sociales"),
]
for slug, title in LEG:
    body = intro(f"{title}.", eyebrow="Legal") + f"""
    <section class="section section--flush-top">
      <div class="container">
        <article class="prose">
{LEGAL[slug]}
        </article>
      </div>
    </section>"""
    write(f"/legal/{slug}/", title, f"{title} de Comercial de Recambios Montemayor, S.L.", "legal", body)

# ---------------------------------------------------------------- otros idiomas (inglés, francés, alemán)
# Portada, productos, empresa y contacto. Los textos están en _fuente/contenido/idiomas.py.

INSTALACIONES_FOTOS = [r for r, _ in INSTALACIONES]   # mismas fotos que en español, con el texto traducido


def cta_int(lang):
    t = I.T[lang]
    return f"""
    <section class="section section--tile center">
      <div class="container">
        <span class="badge-icon" style="margin:0 auto">{icon("handshake")}</span>
        <h2 style="margin-top:28px">{t["cta_titulo"]}</h2>
        <p class="lead" style="max-width:600px;margin:0 auto 28px">{t["cta_texto"]}</p>
        <div class="actions">
          <a class="btn" href="mailto:{EMAIL}?subject={urllib.parse.quote(t["asunto"])}">{icon("mail")} {EMAIL}</a>
          <a class="btn btn--wa" href="{wa(t["wa"])}" target="_blank" rel="noopener">{icon("whatsapp")} WhatsApp</a>
          <a class="more" href="tel:{PHONE_TEL}">{t["llamar"]} {PHONE}</a>
        </div>
      </div>
    </section>"""


def tarjetas_int(lang):
    t, prod = I.T[lang], I.RUTAS[lang]["productos"]
    out = []
    for c in CATEGORIAS:
        fams = c["familias"]
        lista = "".join(f'<li><a href="{prod}#{c["slug"]}">{e(nombre_fam(lang, c["slug"], f))}</a></li>' for f in fams[:5])
        if len(fams) > 5:
            lista += f'<li><a class="catcard__rest" href="{prod}#{c["slug"]}">{t["y_mas"].format(n=len(fams) - 5)}</a></li>'
        out.append(f"""
          <article class="catcard">
            {catcard_head(c["slug"], nombre_cat(lang, c["slug"]), corto_cat(lang, c["slug"]), f'{prod}#{c["slug"]}')}
            <ul class="catcard__list">{lista}</ul>
            <a class="more" href="{prod}#{c["slug"]}">{t["ver_gama"]}</a>
          </article>""")
    return '<div class="catcards">' + "".join(out) + "\n        </div>"


for lang in ("en", "fr", "de"):
    t, rutas = I.T[lang], I.RUTAS[lang]

    # Portada
    datos = "".join(f'<li>{icon(ic)}<strong>{a}</strong><span>{b}</span></li>'
                    for ic, (a, b) in zip(("calendar", "box", "ruler", "award"), t["datos"]))
    body = f"""
    <section class="hero hero--photo" style="--hero-img:url('/assets/img/fondos/campo.webp')">
      <div class="container">
        <span class="eyebrow">{t["hero_eyebrow"]}</span>
        <h1>{t["hero_h1"]}</h1>
        <p class="lead">{t["hero_texto"]}</p>
        <div class="actions">
          <a class="btn" href="{rutas["productos"]}">{t["hero_productos"]}</a>
          <a class="more" href="{rutas["contacto"]}">{t["hero_contacto"]}</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container container--wide">
        <div class="headline">
          <h2>{t["productos_h2"]}</h2>
          <p class="lead">{t["productos_lead"]}</p>
        </div>
        {tarjetas_int(lang)}
      </div>
    </section>
{sectores(lang)}
{video_band("corte-fieltro", t["video_eyebrow"], t["video_titulo"], t["video_texto"],
            f'<a class="btn btn--light" href="{rutas["productos"]}#faldetas">{t["video_boton"]}</a><a class="more" href="{rutas["empresa"]}">{t["video_instalaciones"]}</a>')}

    <section class="section section--tight section--tile">
      <div class="container container--wide">
        <ul class="facts">{datos}</ul>
      </div>
    </section>

    <section class="section section--dark">
      <div class="container center">
        <p class="statement">{t["lema"]} <span>{t["lema_texto"]}</span></p>
        <div class="actions" style="margin-top:32px"><a class="more" href="{rutas["empresa"]}">{t["conocenos"]}</a></div>
      </div>
    </section>
{cta_int(lang)}"""
    write(rutas["inicio"], t["inicio_titulo"], t["inicio_desc"], f"{lang}-inicio", body,
          og_img="assets/img/fondos/campo.webp", og_titulo=t["inicio_og"], og_frase=t["inicio_frase"], lang=lang)

    # Productos
    secciones = []
    for c in CATEGORIAS:
        nombre = nombre_cat(lang, c["slug"])
        fams = "".join(f'<li>{icon(f["icono"])}<span>{e(nombre_fam(lang, c["slug"], f))}</span></li>' for f in c["familias"])
        secciones.append(f"""
        <article class="en-cat" id="{c["slug"]}">
          <div class="en-cat__head">
            {badge(c["icono"])}
            <div>
              <h2>{nombre}</h2>
              <p class="lead">{corto_cat(lang, c["slug"])}</p>
            </div>
          </div>
          <ul class="en-cat__list">{fams}</ul>
          <div class="actions actions--start">
            <a class="btn" href="mailto:{EMAIL}?subject={urllib.parse.quote(t["pedir_asunto"] + nombre)}">{t["pedir"]}</a>
            <a class="more" href="/productos/{c["slug"]}/" hreflang="es">{t["ficha"]}</a>
          </div>
        </article>""")
    body = intro(t["prod_h1"], t["prod_lead"])
    body += f"""
    <section class="section section--flush-top">
      <div class="container">{"".join(secciones)}
      </div>
    </section>""" + cta_int(lang)
    write(rutas["productos"], t["prod_titulo"], t["prod_desc"], f"{lang}-productos", body,
          og_frase=" · ".join(nombre_cat(lang, s) for s, _, _ in PRODUCTS), lang=lang)

    # Empresa
    valores = "".join(f'<li>{badge(ic, "sm")}<h3>{a}</h3><p>{b}</p></li>' for ic, a, b in t["valores"])
    anos = "".join(f'<li><span class="years__num gradient">{a}</span><h3>{h}</h3><p>{p}</p></li>' for a, h, p in t["historia"])
    body = intro(t["emp_h1"], t["emp_lead"], eyebrow=t["emp_eyebrow"])
    body += f"""

    <div class="container container--wide page-photo">{img("assets/img/empresa/oficinas.webp", t["emp_foto"], lazy=False)}</div>

    <section class="section section--flush-top">
      <div class="container">
        <ul class="values">{valores}</ul>
      </div>
    </section>

    <section class="section section--tile">
      <div class="container">
        <div class="headline">
          <h2>{t["inst_h2"]}</h2>
          <p class="lead">{t["inst_lead"]}</p>
        </div>
        {carousel_html("instalaciones", list(zip(INSTALACIONES_FOTOS, t["inst_fotos"])), t["inst_aria"])}
      </div>
    </section>

    <section class="section">
      <div class="container container--wide">
        <div class="headline">
          <h2>{t["historia_h2"]}</h2>
        </div>
        <ol class="years">{anos}</ol>
      </div>
    </section>
{cta_int(lang)}"""
    write(rutas["empresa"], t["emp_titulo"], t["emp_desc"], f"{lang}-empresa", body,
          og_img="assets/img/empresa/oficinas.webp", og_titulo=t["emp_og"], lang=lang)

    # Contacto
    body = intro(t["con_h1"], t["con_lead"], eyebrow="Comercial de Recambios Montemayor S.L.")
    body += f"""
    <section class="section section--flush-top">
      <div class="container container--wide">
        <div class="contact-tiles">
          <a class="contact-tile" href="mailto:{EMAIL}">{badge("mail")}<h3>Email</h3><strong>{EMAIL}</strong><span>{t["con_email_txt"]}</span></a>
          <a class="contact-tile" href="tel:{PHONE_TEL}">{badge("phone")}<h3>{t["con_tel"]}</h3><strong>{PHONE}</strong><span>{t["con_tel_txt"]}</span></a>
          <a class="contact-tile" href="{wa(t["wa"])}" target="_blank" rel="noopener">{badge("whatsapp")}<h3>WhatsApp</h3><strong>+34 {WHATSAPP_VER}</strong><span>{t["con_wa_txt"]}</span></a>
          <a class="contact-tile" href="{DIR}" target="_blank" rel="noopener">{badge("pin")}<h3>{t["con_visita"]}</h3><strong>C/ La Jarra 41</strong><span>P.I. Los Alfares · 14540 La Rambla (Córdoba), {t["pais"]}</span></a>
        </div>
      </div>
    </section>

    <section class="section section--tile">
      <div class="container">
        <div class="headline">
          <h2>{t["horario_h2"]}</h2>
          <p class="lead">{t["horario_lead"]}</p>
        </div>
        <div class="hours">
          <div class="hours__card"><h3>{t["invierno"]}</h3><p>{t["lunes_viernes"]}</p><span class="hours__time">8:30 – 13:30</span><span class="hours__time">16:00 – 19:00</span></div>
          <div class="hours__card"><h3>{t["verano"]}</h3><p>{t["lunes_viernes"]}</p><span class="hours__time">8:00 – 15:00</span></div>
        </div>
      </div>
    </section>"""
    write(rutas["contacto"], t["con_titulo"], t["con_desc"].format(tel=PHONE, mail=EMAIL), f"{lang}-contacto", body,
          og_img="assets/img/empresa/oficinas.webp", og_frase=t["con_frase"].format(tel=PHONE, mail=EMAIL), lang=lang)

# ---------------------------------------------------------------- 404

body = """
    <section class="section error-page">
      <div class="container">
        <span class="error-page__code">404</span>
        <h1 style="font-size:2.2rem">Esta página no existe.</h1>
        <p class="lead">Puede que haya cambiado de dirección.</p>
        <div class="actions">
          <a class="btn" href="/">Ir al inicio</a>
          <a class="more" href="/productos/">Ver productos</a>
        </div>
      </div>
    </section>"""
write("/404", "Página no encontrada", "La página solicitada no existe.", "", body)

# ---------------------------------------------------------------- sitemap
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sitemap += "".join(f"  <url><loc>{SITE}{p}</loc></url>\n" for p in PAGINAS)
sitemap += "</urlset>\n"
open(os.path.join(REPO, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(sitemap)
open(os.path.join(REPO, "robots.txt"), "w", encoding="utf-8", newline="\n").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
print(f"sitemap.xml: {len(PAGINAS)} páginas")
