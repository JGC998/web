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
VERSION = "20261016d"   # súbelo al cambiar CSS o JS para que los navegadores los descarguen de nuevo

# ---------------------------------------------------------------- contenido
_P = json.load(open(os.path.join(FUENTE, "contenido", "productos.json"), encoding="utf-8"))
CATEGORIAS = _P["categorias"]
PRODUCTS = [(c["slug"], c["nombre"], c["intro"]) for c in CATEGORIAS]   # orden del menú
NAMES = {c["slug"]: c["nombre"] for c in CATEGORIAS}
SHORT = {c["slug"]: c["corto"] for c in CATEGORIAS}
CAT_ICON = {c["slug"]: c["icono"] for c in CATEGORIAS}
SEC_ICON = {c["slug"]: {f["slug"]: f["icono"] for f in c["familias"]} for c in CATEGORIAS}
C = {"products": {c["slug"]: [{"slug": f["slug"], "title": f["nombre"]} for f in c["familias"]] for c in CATEGORIAS}}
LEGAL = json.load(open(os.path.join(FUENTE, "contenido", "legal.json"), encoding="utf-8"))
ARCHIVO_NOTICIAS = json.load(open(os.path.join(FUENTE, "contenido", "noticias-archivo.json"), encoding="utf-8"))
NOTICIAS = leer_noticias(FUENTE, REPO)   # carpetas de _fuente/contenido/noticias/
PAGINAS = []                             # rutas generadas, para el sitemap


def img_size(rel):
    with Image.open(os.path.join(REPO, rel)) as im:
        return im.size


def img(rel, alt, cls="", lazy=True):
    w, h = img_size(rel)
    a = f' class="{cls}"' if cls else ""
    l = ' loading="lazy" decoding="async"' if lazy else ""
    return f'<img src="/{rel}" alt="{e(alt)}" width="{w}" height="{h}"{a}{l}>'


def mailto(subject):
    return f"mailto:{EMAIL}?subject={e(subject)}"


def sentence(t):
    """'Materiales para Vulcanizar' -> 'Materiales para vulcanizar' (respeta siglas como PVC)."""
    t = t[0] + t[1:].lower()
    return t.replace("pvc", "PVC")


# ---------------------------------------------------------------- plantilla

def head(title, desc, og_img=None):
    full = f"{title} | CRM Componentes" if title else "CRM Componentes — Comercial de Recambios Montemayor"
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(full)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="theme-color" content="#ffffff">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="es_ES">
  <meta property="og:site_name" content="CRM Componentes">
  <meta property="og:title" content="{e(full)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:image" content="{SITE}/{og_img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="/assets/css/base.css?v={VERSION}">
  <link rel="stylesheet" href="/assets/css/layout.css?v={VERSION}">
  <link rel="stylesheet" href="/assets/css/components.css?v={VERSION}">
  <script src="/assets/js/main.js?v={VERSION}" defer></script>
</head>"""


NAV = [
    ("/", "Inicio", "inicio"),
    ("/productos/", "Productos", "productos"),
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


def header(active):
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


FRASE_COMPARTIR = "Componentes para elevación y transporte · La Rambla (Córdoba)"


def imagen_compartir(path, title, foto=None, frase=None):
    """Genera assets/img/compartir/<página>.jpg y devuelve su ruta."""
    nombre = path.strip("/").replace("/", "-") or "inicio"
    rel = f"assets/img/compartir/{nombre}.jpg"
    generar_imagen_compartir(os.path.join(REPO, rel), title or "CRM Componentes", frase or FRASE_COMPARTIR,
                             foto=os.path.join(REPO, foto) if foto else None,
                             logo=os.path.join(REPO, "assets", "img", "brand", "logo-crm.png"))
    return rel


def write(path, title, desc, active, body, og_img=None, og_titulo=None, og_frase=None):
    """og_img: foto de fondo para la imagen al compartir (si no, fondo verde)."""
    if path == "/404":
        compartir = "assets/img/compartir/inicio.jpg"
    else:
        if path != "/presupuesto/gracias/":   # la página de gracias no va al sitemap
            PAGINAS.append(path)
        compartir = imagen_compartir(path, og_titulo or title, og_img, og_frase)
    out = head(title, desc, compartir) + "\n" + header(active) + '\n  <main id="contenido">' + body + "\n  </main>\n" + FOOTER
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
            {badge(CAT_ICON[s], "sm")}
            <h3><a href="/productos/{s}/">{NAMES[s]}</a></h3>
            <p>{SHORT[s]}</p>
            <ul class="catcard__list">{fams}</ul>
            <a class="more" href="/productos/{s}/">Ver todo</a>
          </article>""")
    return '<div class="catcards">' + "".join(out) + "\n        </div>"


def news_cards(noticias):
    """Tarjetas de noticia con foto de portada, fecha, título y resumen."""
    out = []
    for n in noticias:
        foto = (f'<a class="newscard__media" href="/noticias/{n["slug"]}/" tabindex="-1" aria-hidden="true">'
                f'{img(n["fotos"][0], n["titulo"])}</a>') if n["fotos"] else ""
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


    <section class="section">
      <div class="container container--wide">
        <div class="headline">
          <h2>Nuestros productos.</h2>
          <p class="lead">Todo lo que tu instalación necesita, en un solo proveedor.</p>
        </div>
        {product_tiles()}
      </div>
    </section>
{video_band("corte-fieltro", "Fabricación a medida", "Lo cortamos a tu medida.",
            "Fieltro, goma y caramelo cortados y perforados en nuestras instalaciones de La Rambla.",
            '<a class="btn btn--light" href="/productos/faldetas/">Ver faldetas</a><a class="more" href="/quienes-somos/#instalaciones">Nuestras instalaciones</a>')}

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
    </section>""" + cta()
    names = ", ".join(s["title"].lower() for s in secs)
    fotos_cat = [p for sec in secs for p in section_photos(slug, sec)]
    write(f"/productos/{slug}/", name, f"{name} en CRM (La Rambla, Córdoba): {names}.", f"productos/{slug}", body,
          og_img=fotos_cat[0] if fotos_cat else None, og_frase=SHORT[slug])


for slug, name, intro_text in PRODUCTS:
    product_page(slug, name, intro_text)

# ---------------------------------------------------------------- quiénes somos

body = intro("Una empresa familiar <span class=\"gradient\">desde 1994.</span>", "Pasado, tecnología. Presente, innovación. Futuro, sostenible.",
             eyebrow="Quiénes somos")
INSTALACIONES = [
    ("assets/img/empresa/fachada.webp", "Fachada de CRM en el P.I. Los Alfares"),
    ("assets/img/empresa/cnc-1.webp", "Máquina de corte por control numérico (CNC)"),
    ("assets/img/empresa/corte-cnc-goma.webp", "Corte de goma en la CNC"),
    ("assets/img/empresa/cnc-2.webp", "Cabezal de corte de la CNC"),
    ("assets/img/empresa/alta-frecuencia-1.webp", "Máquina de alta frecuencia para bandas de PVC"),
    ("assets/img/empresa/alta-frecuencia-2.webp", "Soldadura de perfiles en bandas de PVC"),
    ("assets/img/empresa/nave-nueva-1.webp", "Nueva nave en construcción"),
    ("assets/img/empresa/nave-nueva-2.webp", "Estructura de la nueva nave"),
]
body += f"""

    <div class="container container--wide page-photo">{img("assets/img/empresa/fachada.webp", "Nave de CRM en el P.I. Los Alfares, La Rambla", lazy=False)}</div>

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
write("/quienes-somos/", "Quiénes somos", "CRM S.L. es una empresa familiar fundada en 1994 en La Rambla (Córdoba), especializada en componentes para elevación y transporte de materiales.", "quienes-somos", body, og_img="assets/img/empresa/fachada.webp", og_titulo="Una empresa familiar desde 1994")

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
      og_img="assets/img/empresa/fachada.webp", og_frase=f"Teléfono {PHONE} · WhatsApp {WHATSAPP_VER}")

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
