/* =========================================================
   CRM — Prototipos de formato (/nuevo-diseno/*)
   formats.js: panel de navegación entre los 6 prototipos,
   toggles genéricos [data-nav-toggle] y revelado al hacer
   scroll para .rd-reveal (scrollytelling).
   ========================================================= */

(function () {
  "use strict";

  /* ---------- Panel flotante: saltar entre formatos ---------- */
  var PAGES = [
    { id: "clasico", name: "Clásico (5 estilos)", href: "/nuevo-diseno/" },
    { id: "bento", name: "Bento Grid", href: "/nuevo-diseno/bento/" },
    { id: "split-screen", name: "Split-screen fijo", href: "/nuevo-diseno/split-screen/" },
    { id: "app-shell", name: "App-shell con sidebar", href: "/nuevo-diseno/app-shell/" },
    { id: "scrollytelling", name: "Scrollytelling inmersivo", href: "/nuevo-diseno/scrollytelling/" },
    { id: "editorial-revista", name: "Editorial revista", href: "/nuevo-diseno/editorial-revista/" }
  ];

  var currentId = document.body.getAttribute("data-format") || "clasico";

  var wrap = document.createElement("div");
  wrap.className = "rd-fmtnav";
  wrap.setAttribute("data-open", "false");

  var panel = document.createElement("div");
  panel.className = "rd-fmtnav__panel";
  panel.setAttribute("role", "menu");
  panel.setAttribute("aria-label", "Saltar a otro prototipo");

  var title = document.createElement("span");
  title.className = "rd-fmtnav__title";
  title.textContent = "Prototipos";
  panel.appendChild(title);

  PAGES.forEach(function (page) {
    var a = document.createElement("a");
    a.className = "rd-fmtnav__link";
    a.href = page.href;
    a.textContent = page.name;
    if (page.id === currentId) a.setAttribute("aria-current", "page");
    panel.appendChild(a);
  });

  var toggleBtn = document.createElement("button");
  toggleBtn.type = "button";
  toggleBtn.className = "rd-fmtnav__toggle";
  toggleBtn.setAttribute("aria-expanded", "false");
  toggleBtn.innerHTML = '<span class="rd-fmtnav__toggle-dot" aria-hidden="true"></span> Formatos';
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

  wrap.appendChild(panel);
  wrap.appendChild(toggleBtn);
  document.body.appendChild(wrap);

  /* ---------- Toggle genérico (sidebar móvil de app-shell, etc.) ---------- */
  document.querySelectorAll("[data-nav-toggle]").forEach(function (btn) {
    var targetSel = btn.getAttribute("data-nav-toggle");
    var target = targetSel ? document.querySelector(targetSel) : null;
    btn.addEventListener("click", function () {
      var open = document.body.classList.toggle("rd-shell-open");
      btn.setAttribute("aria-expanded", String(open));
      if (target) target.classList.toggle("is-open", open);
    });
  });

  /* ---------- Año en pie ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- Revelado al hacer scroll (.rd-reveal) ---------- */
  var reveals = document.querySelectorAll(".rd-reveal");
  if (reveals.length) {
    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion || !("IntersectionObserver" in window)) {
      reveals.forEach(function (el) { el.classList.add("is-visible"); });
    } else {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.3 }
      );
      reveals.forEach(function (el) { observer.observe(el); });
    }
  }
})();
