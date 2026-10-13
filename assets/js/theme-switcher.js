/* =========================================================
   CRM — Prototipo de rediseño
   theme-switcher.js: menú móvil + selector de los 5 estilos
   en vivo (sin recargar la página, con persistencia).
   ========================================================= */

(function () {
  "use strict";

  var yearEl = document.getElementById("rd-year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- Menú móvil ---------- */
  var navToggle = document.querySelector(".rd-nav-toggle");
  if (navToggle) {
    navToggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("rd-nav-open");
      navToggle.setAttribute("aria-expanded", String(open));
    });
    document.querySelectorAll(".rd-nav__list a").forEach(function (link) {
      link.addEventListener("click", function () {
        document.body.classList.remove("rd-nav-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- Selector de estilos ---------- */
  var THEMES = [
    { id: "theme-01", name: "Minimal Claro", href: "/css/theme-01-minimal.css", color: "#2e9233" },
    { id: "theme-02", name: "Orgánico Moderno", href: "/css/theme-02-organico.css", color: "#2fae62" },
    { id: "theme-03", name: "Neobrutalista", href: "/css/theme-03-neobrutalista.css", color: "#19c37d" },
    { id: "theme-04", name: "Editorial Arquitectura", href: "/css/theme-04-arquitectura.css", color: "#2f6b45" },
    { id: "theme-05", name: "Glass Suave", href: "/css/theme-05-glass.css", color: "#22b573" }
  ];

  var STORAGE_KEY = "rd-theme-href";
  var themeLink = document.getElementById("rd-theme");
  if (!themeLink) return;

  var currentHref = themeLink.getAttribute("href");

  var wrap = document.createElement("div");
  wrap.className = "rd-switcher";
  wrap.setAttribute("data-open", "false");
  wrap.innerHTML =
    '<div class="rd-switcher__panel" role="menu" aria-label="Elegir estilo">' +
    '<span class="rd-switcher__title">Elige un estilo</span>' +
    "</div>" +
    '<button class="rd-switcher__toggle" type="button" aria-expanded="false">' +
    '<span class="rd-switcher__toggle-dot" aria-hidden="true"></span> Estilos' +
    "</button>";
  document.body.appendChild(wrap);

  var panel = wrap.querySelector(".rd-switcher__panel");
  var toggleBtn = wrap.querySelector(".rd-switcher__toggle");

  var buttons = THEMES.map(function (theme) {
    var btn = document.createElement("button");
    btn.className = "rd-switcher__option";
    btn.type = "button";
    btn.setAttribute("role", "menuitemradio");
    btn.setAttribute("aria-pressed", String(theme.href === currentHref));
    btn.innerHTML =
      '<span class="rd-switcher__swatch" style="background:' + theme.color + '" aria-hidden="true"></span>' +
      theme.name;
    btn.addEventListener("click", function () {
      applyTheme(theme);
    });
    panel.appendChild(btn);
    return btn;
  });

  toggleBtn.addEventListener("click", function () {
    var open = wrap.getAttribute("data-open") !== "true";
    wrap.setAttribute("data-open", String(open));
    toggleBtn.setAttribute("aria-expanded", String(open));
  });

  document.addEventListener("click", function (e) {
    if (!wrap.contains(e.target)) {
      wrap.setAttribute("data-open", "false");
      toggleBtn.setAttribute("aria-expanded", "false");
    }
  });

  function applyTheme(theme) {
    themeLink.setAttribute("href", theme.href);
    currentHref = theme.href;
    buttons.forEach(function (btn, i) {
      btn.setAttribute("aria-pressed", String(THEMES[i].href === theme.href));
    });
    try {
      localStorage.setItem(STORAGE_KEY, theme.href);
    } catch (e) {}
  }
})();
