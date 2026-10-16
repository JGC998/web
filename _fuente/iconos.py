"""Iconos de la web: SVG de trazo de 24×24 que toman el color del texto (currentColor).

icon("bucket")          -> <svg class="icon">…</svg>
badge("bucket", "sm")   -> icono dentro de un recuadro verde suave (tamaños: "sm", "", "lg")
"""

ICONS = {
    # --- generales ---
    "phone": '<path d="M5 3.5h3.2l1.6 4.2-2 1.3a10.5 10.5 0 0 0 5.2 5.2l1.3-2 4.2 1.6v3.2a2 2 0 0 1-2 2A15.5 15.5 0 0 1 3 5.5a2 2 0 0 1 2-2z"/>',
    "whatsapp": '<path d="M4 20.5l1.4-4.2A8.6 8.6 0 1 1 8.6 19.4z"/><path d="M9.3 8.4c.2-.4.5-.5.8-.5h.5c.2 0 .4.1.5.3l.8 1.8c.1.2 0 .4-.1.6l-.6.7c-.1.1-.1.3 0 .5a6.6 6.6 0 0 0 2.7 2.5c.2.1.4.1.5-.1l.7-.8c.2-.2.4-.2.6-.1l1.7.8c.2.1.3.3.3.5 0 .6-.3 1.2-.8 1.5-.7.4-1.6.5-2.5.2a10 10 0 0 1-4.9-4.3c-.6-1-.8-2.3-.3-3.1z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
    "pin": '<path d="M12 21s-6.5-6.2-6.5-11.2a6.5 6.5 0 0 1 13 0C18.5 14.8 12 21 12 21z"/><circle cx="12" cy="9.8" r="2.4"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "box": '<path d="M3.5 7.5 12 3.5l8.5 4v9L12 20.5l-8.5-4z"/><path d="M3.5 7.5 12 11.5l8.5-4M12 11.5v9"/>',
    "ruler": '<rect x="2.5" y="8" width="19" height="8" rx="1.5"/><path d="M6.5 8v3M10 8v4.5M13.5 8v3M17 8v4.5"/>',
    "award": '<circle cx="12" cy="9" r="5.5"/><path d="m8.6 13.4-1.4 7.1 4.8-2.5 4.8 2.5-1.4-7.1"/>',
    "doc": '<path d="M6.5 3h7.5l4.5 4.5V21h-12z"/><path d="M14 3v4.5h4.5M9.5 12.5h6M9.5 16.5h6"/>',
    "camera": '<path d="M4 8h3.2L9 5.5h6L16.8 8H20v11H4z"/><circle cx="12" cy="13.3" r="3.3"/>',
    "users": '<circle cx="9" cy="8.5" r="3.3"/><path d="M3 19.5a6 6 0 0 1 12 0"/><circle cx="17" cy="9.5" r="2.4"/><path d="M16.3 14a4.6 4.6 0 0 1 5 4.6"/>',
    "truck": '<path d="M2.5 6.5h11v9.5h-11zM13.5 10h4l3 3.2V16h-7"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    "refresh": '<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M19.5 4.5v4.5H15"/>',
    "handshake": '<path d="M4 5.5h16v10.5H10l-6 4.5z"/><path d="M8 9.5h8M8 12.5h5"/>',
    "wrench": '<path d="M15.5 3.8a4.6 4.6 0 0 0-5.1 6.3l-6.6 6.6a2 2 0 0 0 2.8 2.8l6.6-6.6a4.6 4.6 0 0 0 6.3-5.1l-2.9 2.9-2.4-.6-.6-2.4z"/>',
    # --- productos ---
    "belt": '<circle cx="5.5" cy="12" r="3"/><circle cx="18.5" cy="12" r="3"/><path d="M5.5 9h13M5.5 15h13"/>',
    "belt-incline": '<circle cx="5" cy="15.5" r="2.3"/><circle cx="19" cy="6" r="2.3"/><path d="M3.8 13.5 17.8 4M6.2 17.5l14-9.5"/><path d="M9 15.5V21M16 10.7V21M6.5 21h12"/>',
    "idler": '<path d="M2.5 8.5 6.5 15M21.5 8.5 17.5 15"/><rect x="7" y="13.5" width="10" height="3" rx="1.5"/><path d="M5 20h14M8 16.5V20M16 16.5V20"/>',
    "press": '<rect x="4" y="3.5" width="16" height="4" rx="1"/><rect x="4" y="16.5" width="16" height="4" rx="1"/><path d="M2.5 12h19"/><path d="M8 9.5v1M12 9.5v1M16 9.5v1M8 13.5v1M12 13.5v1M16 13.5v1"/>',
    "staple": '<path d="M2.5 14h19"/><path d="M6.5 19V9a2.5 2.5 0 0 1 2.5-2.5h6A2.5 2.5 0 0 1 17.5 9v10"/>',
    "scraper": '<circle cx="9" cy="9" r="5.5"/><circle cx="9" cy="9" r="1.5"/><path d="M13.2 12.8 18 17.6"/><path d="M15.2 20.4l5.2-5.2"/>',
    "roller": '<rect x="3.5" y="7.5" width="17" height="9" rx="4.5"/><path d="M8 7.5v9"/><path d="M1.5 12h2M20.5 12h2"/>',
    "drum": '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2"/><path d="M1.5 12H5M19 12h3.5"/>',
    "can": '<path d="M6 8h12v11a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z"/><path d="M8.5 8V4.5h7V8"/><path d="M9 13h6M9 16.5h4"/>',
    "parts": '<circle cx="8" cy="8.5" r="4.5"/><circle cx="8" cy="8.5" r="1.7"/><rect x="12.5" y="12" width="8.5" height="8.5" rx="2"/><circle cx="16.75" cy="16.25" r="1.4"/>',
    "sheets": '<path d="M3 9.5 12 5l9 4.5L12 14z"/><path d="m3 13.5 9 4.5 9-4.5"/><path d="m3 17 9 4.5 9-4.5"/>',
    "lagging": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.3"/><path d="M12 3.5V7M12 17v3.5M3.5 12H7M17 12h3.5M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
    "cleated": '<rect x="2" y="14" width="20" height="4.5" rx="2.25"/><path d="M6 14V8.5M12 14V8.5M18 14V8.5"/>',
    "modular": '<rect x="3" y="4.5" width="8" height="6" rx="1.5"/><rect x="13" y="4.5" width="8" height="6" rx="1.5"/><rect x="8" y="13.5" width="8" height="6" rx="1.5"/><path d="M3 16.5h2.5M18.5 16.5H21"/>',
    "chain": '<rect x="2" y="8" width="10" height="8" rx="4"/><rect x="12" y="8" width="10" height="8" rx="4"/><circle cx="7" cy="12" r="1"/><circle cx="17" cy="12" r="1"/>',
    "cord": '<circle cx="6" cy="12" r="3.5"/><circle cx="18" cy="12" r="2.5"/><path d="M6 8.5 18 9.5M6 15.5l12-1"/>',
    "nut": '<path d="m12 3 7.8 4.5v9L12 21l-7.8-4.5v-9z"/><circle cx="12" cy="12" r="3"/>',
    "elevator": '<circle cx="9" cy="5" r="2.5"/><circle cx="9" cy="19" r="2.5"/><path d="M6.5 5v14M11.5 5v14"/><path d="M11.5 7.5h5l-1 3h-4M11.5 13.5h5l-1 3h-4"/>',
    "bucket": '<path d="M3.5 7.5h17l-2.3 10a2 2 0 0 1-2 1.5H7.8a2 2 0 0 1-2-1.5z"/><path d="M3.5 7.5 2.5 5"/><circle cx="9" cy="11.5" r=".6"/><circle cx="15" cy="11.5" r=".6"/>',
    "magnet": '<path d="M5 3.5h4.5V12a2.5 2.5 0 0 0 5 0V3.5H19V12a7 7 0 0 1-14 0z"/><path d="M5 7.5h4.5M14.5 7.5H19"/>',
    "burst": '<rect x="3" y="3" width="18" height="18" rx="2.5"/><path d="m12 7 1.2 2.8 3-.7-1.8 2.5 2.4 1.7-3 .3.2 3-2-2.2-2 2.2.2-3-3-.3 2.4-1.7L7.8 9.1l3 .7z"/>',
    "shield": '<path d="M12 3 19 6v5.5c0 4.5-3 7.8-7 9.5-4-1.7-7-5-7-9.5V6z"/><path d="m9 12 2 2 4-4"/>',
    "bolt": '<path d="M7.5 3.5h9v3.5h-9z"/><path d="M10 7v13.5h4V7"/><path d="m10 10.5 4 1.2M10 14l4 1.2M10 17.5l4 1.2"/>',
    "skirt": '<path d="M2.5 4.5h19"/><path d="M4.5 7.5h15v10c-2.5 1.6-5 1.6-7.5 0s-5-1.6-7.5 0z"/><circle cx="8" cy="10.5" r="1"/><circle cx="12" cy="10.5" r="1"/><circle cx="16" cy="10.5" r="1"/><path d="M8 4.5v3M16 4.5v3"/>',
    "amber": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m7 15.5 4-7M11 15.5l4-7"/>',
    "felt": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 9h.01M11 9h.01M15 9h.01M9 12h.01M13 12h.01M17 12h.01M7 15h.01M11 15h.01M15 15h.01" stroke-width="2.2"/>',
    "star": '<path d="m12 3 2 3.6 4-.9-.9 4L21 12l-3.9 2.3.9 4-4-.9L12 21l-2-3.6-4 .9.9-4L3 12l3.9-2.3-.9-4 4 .9z"/><circle cx="12" cy="12" r="2.2"/>',
    "wave": '<path d="M3 6h18v8c-1.5 2-3 2-4.5 0s-3-2-4.5 0-3 2-4.5 0-3-2-4.5 0z"/><path d="M3 9.5h18"/>',
    "net": '<rect x="3" y="3" width="18" height="18" rx="2.5"/><path d="M3 9 9 3M3 15 15 3M3 21 21 3M9 21 21 9M15 21l6-6M3 3l18 18M3 9l12 12M9 3l12 12"/>',
    "block": '<rect x="5" y="3.5" width="14" height="17" rx="2.5"/><circle cx="12" cy="9" r="2.3"/><path d="M9 15.5h6"/>',
}


def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def badge(name, size=""):
    mod = f" badge-icon--{size}" if size else ""
    return f'<span class="badge-icon{mod}">{icon(name)}</span>'
