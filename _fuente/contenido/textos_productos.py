"""Textos técnicos de cada familia de producto (HTML) y tablas.

TEXT[categoria][familia] -> HTML que aparece al abrir la familia.
EXTRA[(categoria, familia)] -> contenido adicional a ancho completo (tablas técnicas).
Si una familia no tiene texto, la web muestra "Consúltanos medidas, calidades y disponibilidad."
"""
from html import escape as e

# ---------------------------------------------------------------- productos

def tags(*items):
    return '<ul class="tags">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def table(caption, cols, rows, first_th=True):
    th = "".join(f'<th scope="col">{c}</th>' for c in cols)
    body = []
    for r in rows:
        cells = []
        for i, v in enumerate(r):
            if v == "Sí":
                v = '<span class="badge-yes">Sí</span>'
            elif v == "No":
                v = '<span class="badge-no">No</span>'
            cells.append(f'<th scope="row">{v}</th>' if i == 0 and first_th else f"<td>{v}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"""<div class="table-wrap"><table class="spec-table">
          <caption>{caption}</caption>
          <thead><tr>{th}</tr></thead>
          <tbody>{"".join(body)}</tbody>
        </table></div>"""


TEXT = {
    "bandas-transportadoras": {
        "bandas-transportadoras": f"""
<h3>Bandas transportadoras lisas</h3>
<p>Disponemos de un amplio stock permanente para entrega inmediata, tanto de metrajes como de bobinas completas. Nuestro stock consta de bandas de anchos desde 400 hasta 1200 mm; para otros anchos disponemos de stock en la fábrica de Francia.</p>
<p><strong>Resistencias:</strong> 250/2 · 400/3 · 500/4 · 630/4 · 800/4<br><strong>Recubrimientos:</strong> 3+1,5 · 4+2 · 6+2 · 8+3</p>
<p>Otros recubrimientos y resistencias, bajo pedido.</p>
{tags("Antiabrasiva y antiaceite G", "Antillama K", "Alimentaria FDA")}
<h3>Bandas transportadoras nervadas</h3>
<p>Para el transporte de materiales con inclinaciones moderadas —que, dependiendo del tipo de material, su granulometría y, sobre todo, su forma, puede llegar hasta los 45º— aconsejamos utilizar la banda nervada estándar, con nervios de 14 mm de altura.</p>
<p>Este tipo de banda, con la carcasa y el recubrimiento adecuados para cada instalación y material a transportar, es la de mayor uso por ser la primera de la serie de nervios, y ha sido utilizada con éxito probado en los más variados tipos de transportes inclinados de tipo general.</p>
<p><strong>Ancho:</strong> de 400 a 1000 mm · <strong>Resistencia:</strong> 400/3 · <strong>Altura de taco:</strong> 14 mm</p>
{tags("Antiabrasivas", "Alimentaria", "Antiaceite")}
<h3>Bandas transportadoras Chevron</h3>
<p>Para ángulos de transporte elevados recomendamos el uso de la banda Chevron, con un taco de 25 mm o 32 mm de altura. Su construcción permite el transporte en ángulos superiores a 30º, con dos importantes particularidades:</p>
<ul>
<li>Posibilidad de colocar baberos en la zona lisa lateral, evitando que se produzcan pérdidas de material en las cargas.</li>
<li>Evacuación de agua en la zona de separación entre los nervios centrales, de 4 mm de ancho.</li>
</ul>""",
        "estaciones": """
<p>Consulta nuestra gama de soportes y estaciones para rodillos en <a href="http://www.soportespararodilloscrm.com" target="_blank" rel="noopener">www.soportespararodilloscrm.com</a>.</p>""",
        "grapas": f"""
<h3>Grapas de reparación</h3>
<p>Las grapas de reparación son muy efectivas cuando se detecta un corte en la banda: antes de que la banda se rompa y produzca una parada, y hasta su posible reparación o sustitución, puede seguir trabajando colocando las grapas, ya que son muy fáciles de montar.</p>
<ul>
<li><strong>C140</strong> — espesor de banda de 5 a 11 mm</li>
<li><strong>C190</strong> — espesor de banda de 8 a 14 mm</li>
<li><strong>C002</strong> — espesor de banda de 14 a 21 mm</li>
</ul>
<p>Existen llaves para estas grapas y rompedores para el sobrante del tornillo. Estas grapas también se pueden utilizar para realizar un empalme en las bandas transportadoras.</p>
<h3>Grapas para realización de empalme</h3>
<p>Se emplean en bandas tanto de goma como de PVC. Modelos con máquina con grapa incorporada o de remaches de cobre para montaje manual.</p>
{tags("Grapa con remaches", "Grapa para máquina")}
<p>Las grapas se fabrican en inoxidable y galvanizado.</p>""",
        "limpiadores-de-bandas": """
<p>En nuestra gama podrá encontrar modelos para bandas lisas:</p>
<h3>Primarios</h3>
<p>Rascador de poliuretano para limpieza en cabeza.</p>
<h3>Secundarios</h3>
<p>Para la limpieza en cualquier punto inferior de la banda.</p>
<h3>Materiales</h3>
<p>Poliuretano, goma, polietileno.</p>
<p class="note">Para bandas nervadas disponemos de limpiadores de dedos y cepillos.</p>
<p>Limpiadores internos de bandas para evitar la acumulación de material en los tambores traseros, y así no tener problemas de alineación y roturas en los empalmes.</p>""",
        "rodillos": """
<h3>Barras de impacto</h3>
<p>Las barras de impacto se utilizan para sustituir los rodillos amortiguadores en las zonas de carga.</p>
<p>No solo absorben los impactos, sino que realizan una labor de encauzamiento del material a transportar: al ser una pieza longitudinal no quedan espacios como entre rodillos, por lo que no hay pérdidas ni atranques.</p>
<h3>Rodillo metálico</h3>
<p>Suministramos rodillos fabricados a medida, en serie ligera y pesada: lisos, limpiadores, amortiguadores y guías.</p>""",
        "tambores": """
<p>En CRM diseñamos y fabricamos tambores de cabeza (rodillos motrices) y tambores de cola capaces de soportar las más duras condiciones y ambientes de trabajo de su transportador de banda, ofreciéndole el mejor desempeño y la máxima fiabilidad.</p>
<p>La alta concentricidad de los cilindros nos permite ofrecer tambores de excelente desempeño gracias a un elevado contacto con la cinta, las menores deflexiones del eje y la mínima tensión en los soportes.</p>
<p>Consulta también nuestros <a href="#recubrimientos">recubrimientos y engomado de tambores</a>.</p>""",
        "materiales-para-vulcanizar": """
<h3>Material para la reparación y vulcanización, tanto en frío como en caliente</h3>
<ul>
<li>Parche de rombo</li>
<li>Parche de tiras</li>
<li>Pegamento con endurecedor</li>
<li>Imprimación</li>
<li>Disolución en caliente (5 l y 25 l)</li>
<li>Goma de unión 0,8 mm × 500 de ancho</li>
<li>Goma de unión 2 mm × 500 de ancho</li>
</ul>""",
        "piezas-de-goma": """
<p>Podemos producir cualquier pieza de goma, en diferentes calidades.</p>
<p>Se pueden servir en las formas deseadas, y se pueden fabricar troqueladas, inyectadas o fundidas.</p>""",
        "planchas-de-goma": f"""
<p>Podemos ofrecerle una amplia gama de planchas de goma, que podemos servirle cortadas a anchos y longitudes y en la calidad solicitada.</p>
<h3>Calidades</h3>
{tags("Alimentarias", "Antiaceites", "Antiabrasivas", "Temperatura")}
<h3>Colores</h3>
{tags("Caramelo", "Verde", "Negra", "Roja", "Blanca")}
<p>Podemos servir planchas completas en formatos de 1000, 1400 y 2000 mm de ancho, y 5, 10 y 20 metros de longitud (otras longitudes bajo pedido). Espesores desde 1 a 50 mm en la calidad solicitada.</p>
<p>También fabricamos las piezas solicitadas bajo plano o muestra, con corte y perforado.</p>""",
        "recubrimientos": """
<h3>Engomado de tambores</h3>
<ul>
<li><strong>En caliente</strong>, mediante autoclave.</li>
<li><strong>En frío</strong>, mediante gomas preparadas para su aplicación con pegamento de dos componentes.</li>
<li>Goma con y sin chapa para el recubrimiento de tolvas.</li>
</ul>
<h3>Slide-Lag</h3>
<p>Recubrimiento mecánico de sectores montados sobre guías intercambiables.</p>
<h3>Cerámico</h3>
<p>Recubrimiento de goma con inserción de pieza cerámica para aumentar la tracción del tambor.</p>""",
    },
    "bandas-pvc": {
        "bandas-de-pvc": """
<p>Las bandas de PVC se utilizan para aplicaciones ligeras de transporte de materiales alimentarios, así como en procesos industriales con propiedades químicas.</p>
<p>Las bandas pueden ser lisas, con recubrimientos, espesores y terminaciones diferentes.</p>
<p>Se pueden servir con tacos, guías y runners, así como cerradas sinfín en caliente o con grapas galvanizadas o inoxidables.</p>""",
    },
    "elevacion": {
        "bandas-elevadoras": f"""
<p>Las bandas elevadoras pueden ser de goma o PVC, con diferentes resistencias y calidades:</p>
{tags("Antiaceites", "Alimentarias", "Antiabrasivas", "Antiestáticas", "Temperatura")}
<p>Y la <strong>Superbelt</strong>, con las características de todas ellas en una sola.</p>
<p>En calidad alimentaria disponemos de servicio de corte, tanto longitudinal como transversal, al ancho solicitado por el cliente. También tenemos servicio de perforación para bandas elevadoras.</p>
<p><strong>Resistencias disponibles:</strong> 400/3 · 630/3 · 630/4 · 800/4 · 1000/4</p>""",
        "cangilones": """
<p>Disponemos de una amplia gama de cangilones para elevador fabricados en Europa. Tenemos stock tanto de cangilón plástico como metálico, modelos Eurojet y Jet en diferentes capacidades. Medidas estándar, y se pueden fabricar a medida.</p>
<h3>Cangilón de plástico</h3>
<ul>
<li><strong>PE · Polietileno de alta densidad:</strong> buenas características para aplicaciones de productos alimentarios como harinas, cereales y productos poco abrasivos.</li>
<li><strong>PU · Poliuretano:</strong> productos abrasivos con poco impacto; su otra gran aplicación es para productos pegajosos o húmedos.</li>
<li><strong>PA · Poliamida:</strong> muy apropiado para productos abrasivos como arroz, azúcar, abonos o sal.</li>
</ul>
<h3>Cangilón metálico</h3>
<p>Son cangilones más resistentes y pesados, con una durabilidad superior a los de plástico. Se fabrican en acero al carbono e inoxidable.</p>
<p>Modelos estándar tanto en plástico como metálicos. Tipo C: cangilón de media carga, que facilita su descarga por su poca profundidad de carga.</p>""",
        "imanes": """
<p>Tubos magnéticos, parrillas e imanes automáticos.</p>""",
        "paneles-de-explosion": """
<p>Los paneles de venteo contra explosiones responden a las exigencias esenciales de seguridad y salud de los equipos destinados a ser utilizados en atmósferas explosivas (Directiva 94/9/CE).</p>
<p>En caso de deflagración, los paneles contra explosión están concebidos para evacuar la presión, las llamas y el polvo, protegiendo así a las personas y los equipamientos industriales.</p>
<p>Sistema de protección simple y eficaz: los paneles resisten la depresión y los ciclos de descolmatado neumático, para las utilizaciones corrientes en silos, tolvas, filtros y ciclones.</p>""",
        "sistemas-de-seguridad": f"""
<p>Sensores y detectores para el control y la protección de elevadores y transportadores:</p>
{tags("Detectores de alineación", "Sensores de giro", "Sensores de nivel", "Sensores de temperatura")}""",
        "tornillos-y-grapas": """
<h3>Tornillos para cangilones</h3>
<p>Disponemos de tornillos de cangilón zincados y en acero inoxidable, con tuerca normal o autoblocante y con arandelas planas o cóncavas.</p>
<p>Medidas según normas DIN, disponibles en galvanizado e inoxidable. Las tuercas pueden servirse autoblocantes o normales; las arandelas suelen servirse cóncavas, pero también están disponibles planas.</p>
<h3>Grapas de unión</h3>
<p>Disponemos de grapas de unión para banda elevadora, fabricadas en segmentos para adecuarse a cada ancho y resistencia de banda, en galvanizado o inoxidable dependiendo de su aplicación.</p>
<p>Dependiendo de la resistencia de la banda se debe montar la grapa adecuada:</p>
<ul>
<li><strong>Supergrip nº 1</strong> — hasta 630 N/mm de resistencia</li>
<li><strong>Supergrip nº 2</strong> — hasta 1250 N/mm de resistencia</li>
</ul>""",
        "cadenas-transportadoras": """
<p>Su principal ventaja consiste en poseer un diámetro (C) de rodillo mayor al ancho (A) de la placa; así la cadena logra deslizarse con suavidad y sin rozamientos excesivos.</p>
<p>Se puede proveer con aletas, con pernos salientes, agujeros en las mallas laterales o cualquier otro aditamento, a ubicar según cada necesidad. Los pernos y aletas normalizados se detallan en el catálogo.</p>""",
    },
    "faldetas": {
        "faldetas": """
<p>Con varios fabricantes de bandas europeos hemos confeccionado una nueva generación de gomas para las faldetas de los vibradores.</p>
<p>Disponemos de las faldetas estándar y las nuevas súper antiabrasivas. También estamos desarrollando nuevos modelos que se adapten mejor a los tacos y resistan más rozamiento, con más recubrimiento de goma y menos lonas, pero más resistentes.</p>""",
    },
}

EXTRA = {  # contenido a ancho completo bajo la galería
    ("bandas-pvc", "bandas-de-pvc"): table(
        "Bandas de PVC",
        ["Modelo", "Color", "Espesor", "Telas", "Recubrimientos", "Mín. tambor", "Alimentaria"],
        [
            ["V-2", "Verde", "2 mm", "2", "PVC / Tejido", "50 mm", "No"],
            ["V-3", "Verde", "3 mm", "2", "PVC / Tejido", "80 mm", "No"],
            ["VL-2", "Verde", "2 mm", "2", "PVC / Tejido", "50 mm", "No"],
            ["VG-3", "Verde", "3 mm", "2", "PVC / PVC grabado", "80 mm", "No"],
            ["VR", "Verde", "5 mm", "2", "PVC rugoso / Tejido", "60 mm", "No"],
            ["B-2", "Blanco", "2 mm", "2", "PVC / Tejido", "50 mm", "Sí"],
            ["B-3", "Blanco", "3 mm", "2", "PVC / Tejido", "80 mm", "Sí"],
            ["BB-2", "Blanco", "5 mm", "2", "PVC / PVC", "80 mm", "Sí"],
            ["BB-3", "Blanco", "6 mm", "3", "PVC / PVC", "100 mm", "Sí"],
            ["BD", "Blanco", "4 mm", "2", "PVC dentado / Tejido", "80 mm", "Sí"],
        ],
    )
    + '<div class="grid grid--2">'
    + table("Perfiles", ["Modelo", "Color", "Mín. tambor"],
            [[m, "Verde / Blanco", t] for m, t in [("X-6", "25 mm"), ("Y-8", "50 mm"), ("Z-10", "70 mm"), ("A-13", "90 mm"), ("B-17", "100 mm")]])
    + table("Tacos", ["Modelo", "Color", "Mín. tambor"],
            [[m, "Verde / Blanco", t] for m, t in [("R-20", "120 mm"), ("R/I-30", "120 mm"), ("R/I-40", "120 mm"), ("R/I-50", "150 mm"), ("R/I-60", "150 mm"), ("R-80", "180 mm")]])
    + "</div>",
    ("faldetas", "faldetas"): table(
        "Datos técnicos para la fabricación de faldetas",
        ["Recubrimientos", "Lonas", "Espesores"],
        [["2+1", "2", "6 mm"], ["3+1,5", "3", "8 mm"], ["4+2", "4", "10 mm"], ["6+2", "4", "12/13 mm"], ["8+3", "4", "14/15 mm"]],
    )
    + '<p class="note">Se pueden fabricar en otros espesores. Tolerancias ± 1 mm.</p>',
}

# Familias añadidas con las fotos nuevas de CRM
TEXT["faldetas"].update({
    "estrellas": """
<p>Piezas de goma en forma de estrella, cortadas a medida en diferentes calidades y espesores.</p>
<p>Consúltanos medidas y disponibilidad.</p>""",
    "borde-ondulado": """
<p>Piezas de goma con borde ondulado, fabricadas a medida.</p>
<p>Consúltanos medidas y disponibilidad.</p>""",
    "red": """
<p>Novedad en nuestra gama de faldetas.</p>
<p>Consúltanos medidas y disponibilidad.</p>""",
})

# Las dos tablas de perfiles y tacos van en dos columnas
EXTRA = {k: v.replace('<div class="grid grid--2">', '<div class="tables-2">') for k, v in EXTRA.items()}
