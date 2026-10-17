"""Sectores (páginas /sectores/<slug>/) y campañas de temporada de la portada.

Cada sector lista los productos que le interesan: (categoría, familia) de productos.json.
Si un sector tiene "campana", la portada muestra su aviso desde el día "desde" (mes-día)
hasta que empieza la campaña siguiente. El cambio lo hace el navegador según la fecha,
así que la portada cambia sola aunque no se vuelva a publicar la web.

Para cambiar las fechas o los textos de una campaña, edita aquí y vuelve a publicar.
"""

SECTORES = [
    {
        "slug": "olivar",
        "nombre": "Olivar",
        "nombre_en": "Olive groves",
        "icono": "olive",
        "foto": "assets/img/sectores/olivar.webp",
        "foto_grande": "assets/img/sectores/olivar-campo.webp",
        "titulo": "Faldetas y componentes para vibradores de olivar",
        "descripcion": "Faldetas de goma, fieltro y caramelo, red, estrellas y cierre de tronco para vibradores de olivar, y bandas para almazaras. Stock en La Rambla (Córdoba).",
        "intro": "Todo para que el vibrador trabaje la campaña entera sin paradas: faldetas en goma, fieltro y caramelo, y las piezas que más se desgastan.",
        "texto": """
<p>Fabricamos faldetas para vibradores de olivar en nuestras instalaciones de La Rambla (Córdoba), en goma, fieltro y caramelo, en los espesores y lonas que necesites. Trabajamos con fabricantes europeos de bandas para conseguir gomas más resistentes al rozamiento.</p>
<p>También suministramos bandas transportadoras para almazaras y patios de recepción, en calidad alimentaria.</p>""",
        "productos": [
            ("faldetas", "faldetas"), ("faldetas", "goma"), ("faldetas", "fieltro"), ("faldetas", "caramelo"),
            ("faldetas", "red"), ("faldetas", "estrellas"), ("faldetas", "cierre-tronco"),
            ("faldetas", "borde-ondulado"), ("faldetas", "tacos"),
            ("bandas-transportadoras", "bandas-transportadoras"),
        ],
        "campana": {
            "desde": "10-01",
            "nombre": "Campaña de la aceituna",
            "titulo": "Faldetas para la campaña, en stock.",
            "texto": "Faldetas de goma, fieltro y caramelo y repuestos para vibradores de olivar. Pídelas por WhatsApp y te las preparamos.",
            "whatsapp": "Hola, quería información de faldetas para la campaña de la aceituna.",
        },
    },
    {
        "slug": "almendro",
        "nombre": "Almendro",
        "nombre_en": "Almond orchards",
        "icono": "almond",
        "foto": None,   # pendiente: foto de almendro
        "titulo": "Componentes para la recolección de la almendra",
        "descripcion": "Faldetas y componentes para vibradores y bandas para la recolección y el procesado de la almendra. CRM, La Rambla (Córdoba).",
        "intro": "Componentes para vibradores y bandas para la recolección y el procesado de la almendra.",
        "texto": """
<p>Fabricamos a medida faldetas en goma, fieltro y caramelo, y suministramos bandas transportadoras y bandas de PVC para la recolección, la limpieza y el procesado de la almendra.</p>
<p>Cuéntanos qué máquina tienes y te ayudamos a elegir.</p>""",
        "productos": [
            ("faldetas", "faldetas"), ("faldetas", "goma"), ("faldetas", "fieltro"), ("faldetas", "caramelo"),
            ("bandas-transportadoras", "bandas-transportadoras"), ("bandas-pvc", "bandas-de-pvc"),
        ],
        "campana": {
            "desde": "06-01",
            "nombre": "Campaña de la almendra",
            "titulo": "Prepara la máquina para la almendra.",
            "texto": "Faldetas, bandas y repuestos para la recolección y el procesado de la almendra. Consúltanos por WhatsApp.",
            "whatsapp": "Hola, quería información para la campaña de la almendra.",
        },
    },
    {
        "slug": "ajo",
        "nombre": "Ajo",
        "nombre_en": "Garlic",
        "icono": "garlic",
        "foto": "assets/img/sectores/ajos.webp",
        "titulo": "Bandas para el ajo: limpieza, selección y envasado",
        "descripcion": "Bandas de PVC a medida, bandas modulares y bandas transportadoras para la limpieza, selección y envasado del ajo. CRM, La Rambla (Córdoba).",
        "intro": "Bandas de PVC fabricadas a medida para la limpieza, la selección y el envasado del ajo y otras hortalizas.",
        "texto": """
<p>Fabricamos bandas de PVC a medida en nuestras instalaciones, con tacos, perfiles y bordes soldados por alta frecuencia, cerradas sinfín o con grapas. Bandas alimentarias e industriales para líneas de limpieza, selección, calibrado y envasado.</p>
<p>También suministramos bandas modulares, cordones y correas, y bandas transportadoras de goma.</p>""",
        "productos": [
            ("bandas-pvc", "bandas-de-pvc"), ("bandas-pvc", "bandas-modulares"), ("bandas-pvc", "cordones-y-correas"),
            ("bandas-pvc", "grapas"), ("bandas-transportadoras", "bandas-transportadoras"),
        ],
        "campana": {
            "desde": "03-01",
            "nombre": "Campaña del ajo",
            "titulo": "Bandas a medida para el ajo.",
            "texto": "Bandas de PVC para limpieza, selección y envasado, fabricadas a medida en nuestras instalaciones. Pídenos presupuesto por WhatsApp.",
            "whatsapp": "Hola, quería información de bandas para la campaña del ajo.",
        },
    },
    {
        "slug": "cereal-y-silos",
        "nombre": "Cereal y silos",
        "nombre_en": "Grain and silos",
        "icono": "elevator",
        "foto": "assets/img/sectores/girasol.webp",
        "titulo": "Componentes para elevadores de cangilones y silos",
        "descripcion": "Bandas elevadoras, cangilones, imanes, paneles de explosión y sistemas de seguridad para silos y plantas de cereal. CRM, La Rambla (Córdoba).",
        "intro": "Bandas elevadoras, cangilones y todo lo necesario para elevadores de cangilones en silos y plantas de cereal.",
        "texto": """
<p>Suministramos bandas elevadoras de goma y PVC, con servicio de corte y perforado, cangilones de plástico y metálicos fabricados en Europa, tornillería y grapas de unión.</p>
<p>Y para la seguridad de la instalación: imanes, paneles de venteo contra explosiones y sensores de alineación, giro, nivel y temperatura.</p>""",
        "productos": [
            ("elevacion", "bandas-elevadoras"), ("elevacion", "cangilones"), ("elevacion", "tornillos-y-grapas"),
            ("elevacion", "imanes"), ("elevacion", "paneles-de-explosion"), ("elevacion", "sistemas-de-seguridad"),
        ],
    },
    {
        "slug": "industria",
        "nombre": "Industria, canteras y reciclaje",
        "nombre_en": "Industry, quarries and recycling",
        "icono": "belt-incline",
        "foto": "assets/img/sectores/industria.webp",
        "titulo": "Bandas transportadoras para industria, canteras y reciclaje",
        "descripcion": "Bandas transportadoras antiabrasivas, antiaceite y antillama, rodillos, tambores, limpiadores y vulcanizados para canteras, reciclaje e industria. CRM, La Rambla (Córdoba).",
        "intro": "Bandas transportadoras y todos sus componentes para canteras, plantas de reciclaje e industria.",
        "texto": """
<p>Stock permanente de bandas transportadoras en anchos de 400 a 1200 mm, en calidades antiabrasiva, antiaceite (plantas de RSU y reciclaje) y antillama (siderurgia y productos calientes).</p>
<p>Y todo lo que rodea a la banda: estaciones, rodillos, tambores y su recubrimiento, limpiadores, vulcanizados y planchas de goma.</p>""",
        "productos": [
            ("bandas-transportadoras", "bandas-transportadoras"), ("bandas-transportadoras", "vulcanizados"),
            ("bandas-transportadoras", "rodillos"), ("bandas-transportadoras", "tambores"),
            ("bandas-transportadoras", "limpiadores-de-bandas"), ("bandas-transportadoras", "recubrimientos"),
            ("bandas-transportadoras", "planchas-de-goma"), ("bandas-transportadoras", "estaciones"),
        ],
    },
]
