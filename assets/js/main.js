/* =========================================================
   CRM — Comercial de Recambios Montemayor
   Interacciones: menú móvil, visor de fotos, mapa y
   acordeones de producto
   ========================================================= */

(function () {
  "use strict";

  /* ---------- Año actual en el pie ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  var mobile = window.matchMedia("(max-width: 900px)");
  var nav = document.getElementById("menu");

  /* ---------- Menú de productos en escritorio (panel desplegable) ---------- */
  var megaItem = document.querySelector(".nav__item--mega");
  var megaLink = megaItem && megaItem.querySelector(".nav__link--mega");
  var megaTimer = null;
  var lastPointer = "mouse";

  var openMega = function () {
    if (!megaItem || mobile.matches) return;
    clearTimeout(megaTimer);
    megaItem.classList.add("is-open");
    document.body.classList.add("mega-open");
    megaLink.setAttribute("aria-expanded", "true");
  };

  var closeMega = function () {
    if (!megaItem) return;
    clearTimeout(megaTimer);
    megaItem.classList.remove("is-open");
    document.body.classList.remove("mega-open");
    megaLink.setAttribute("aria-expanded", "false");
  };

  if (megaItem) {
    document.addEventListener("pointerdown", function (e) { lastPointer = e.pointerType; }, true);
    megaItem.addEventListener("mouseenter", openMega);
    megaItem.addEventListener("mouseleave", function () {
      megaTimer = setTimeout(closeMega, 180);
    });
    megaItem.addEventListener("focusin", openMega);
    megaItem.addEventListener("focusout", function (e) {
      if (!megaItem.contains(e.relatedTarget)) closeMega();
    });
    // En tablet (sin ratón) el primer toque abre el panel y el segundo navega
    megaLink.addEventListener("click", function (e) {
      if (!mobile.matches && lastPointer === "touch" && !megaItem.classList.contains("is-open")) {
        e.preventDefault();
        openMega();
      }
    });
    document.querySelector(".nav-scrim").addEventListener("click", closeMega);
  }

  /* ---------- Menú móvil (con niveles: Menú › Productos › Categoría) ---------- */
  var toggle = document.querySelector(".nav-toggle");

  var resetDrill = function () {
    if (!nav) return;
    nav.querySelectorAll(".mega.is-open, .mega__sub.is-open").forEach(function (panel) {
      panel.classList.remove("is-open");
    });
  };

  var closeMenu = function () {
    document.body.classList.remove("nav-open");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
    resetDrill();
  };

  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(open));
      if (!open) resetDrill();
    });
  }

  if (nav) {
    nav.addEventListener("click", function (e) {
      if (!mobile.matches) return;
      var back = e.target.closest("[data-drill-back]");
      if (back) {
        back.closest(".mega__sub, .mega").classList.remove("is-open");
        return;
      }
      var drill = e.target.closest("[data-drill]");
      if (drill) {
        var panel = document.getElementById(drill.getAttribute("data-drill"));
        if (!panel) return;
        e.preventDefault();
        nav.scrollTop = 0;
        var parent = drill.closest(".mega");
        if (parent) parent.scrollTop = 0;
        panel.classList.add("is-open");
      }
    });
  }

  // Al pasar de móvil a escritorio (o al revés) se cierra todo
  var onResize = function () {
    closeMenu();
    closeMega();
  };
  if (mobile.addEventListener) mobile.addEventListener("change", onResize);

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (megaItem && megaItem.classList.contains("is-open")) {
      closeMega();
      megaLink.focus();
    }
    closeMenu();
  });

  /* ---------- Visor de fotos ----------
     Las fotos de cada galería son enlaces ocultos:
       <a href="foto.jpg" data-gallery="nombre" data-alt="Descripción" hidden></a>
     y se abren con un botón:
       <button data-open-gallery="nombre">Ver fotos</button> */
  var hasDialog = typeof HTMLDialogElement === "function";
  if (hasDialog && document.querySelector("[data-gallery]")) {
    var dialog = document.createElement("dialog");
    dialog.className = "lightbox";
    dialog.setAttribute("aria-label", "Fotos");
    dialog.innerHTML =
      '<img class="lightbox__img" alt="">' +
      '<button class="lightbox__btn lightbox__close" type="button" aria-label="Cerrar">&times;</button>' +
      '<button class="lightbox__btn lightbox__prev" type="button" aria-label="Anterior">&#8249;</button>' +
      '<button class="lightbox__btn lightbox__next" type="button" aria-label="Siguiente">&#8250;</button>' +
      '<span class="lightbox__count"></span>';
    document.body.appendChild(dialog);

    var img = dialog.querySelector(".lightbox__img");
    var count = dialog.querySelector(".lightbox__count");
    var prev = dialog.querySelector(".lightbox__prev");
    var next = dialog.querySelector(".lightbox__next");
    var items = [];
    var index = 0;

    var show = function (i) {
      index = (i + items.length) % items.length;
      img.src = items[index].href;
      img.alt = items[index].getAttribute("data-alt") || "";
      count.textContent = items.length > 1 ? index + 1 + " / " + items.length : "";
      prev.hidden = next.hidden = items.length < 2;
    };

    var open = function (name, start) {
      items = Array.prototype.slice.call(document.querySelectorAll('[data-gallery="' + name + '"]'));
      if (!items.length) return;
      show(start || 0);
      dialog.showModal();
    };

    document.addEventListener("click", function (e) {
      var trigger = e.target.closest("[data-open-gallery], a[data-gallery]");
      if (!trigger) return;
      e.preventDefault();
      if (trigger.hasAttribute("data-open-gallery")) {
        open(trigger.getAttribute("data-open-gallery"), 0);
      } else {
        var name = trigger.getAttribute("data-gallery");
        open(name, Array.prototype.indexOf.call(document.querySelectorAll('[data-gallery="' + name + '"]'), trigger));
      }
    });

    prev.addEventListener("click", function () { show(index - 1); });
    next.addEventListener("click", function () { show(index + 1); });
    dialog.querySelector(".lightbox__close").addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog) dialog.close();
    });
    dialog.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") show(index - 1);
      if (e.key === "ArrowRight") show(index + 1);
    });
    dialog.addEventListener("close", function () { img.removeAttribute("src"); });

    // Deslizar con el dedo en el móvil
    var startX = null;
    dialog.addEventListener("touchstart", function (e) { startX = e.touches[0].clientX; }, { passive: true });
    dialog.addEventListener("touchend", function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
      startX = null;
    });
  }

  /* ---------- Mapa: solo se carga al pulsar (sin cookies de Google hasta entonces) ---------- */
  document.querySelectorAll("[data-map-src]").forEach(function (map) {
    map.querySelector("button").addEventListener("click", function () {
      var iframe = document.createElement("iframe");
      iframe.src = map.getAttribute("data-map-src");
      iframe.title = map.getAttribute("data-map-title") || "Mapa";
      iframe.loading = "lazy";
      iframe.referrerPolicy = "no-referrer-when-downgrade";
      iframe.allowFullscreen = true;
      map.innerHTML = "";
      map.appendChild(iframe);
    });
  });

  /* ---------- Acordeones de producto: abrir la sección enlazada ----------
     Si un enlace (#tacos, la rejilla "Explora la gama", URLs antiguas
     redirigidas…) apunta a un <details> cerrado, se abre antes de saltar. */
  var openFromHash = function (hash) {
    if (!hash || hash.length < 2) return null;
    var target = document.getElementById(decodeURIComponent(hash.slice(1)));
    var details = target && target.closest("details");
    if (details && !details.open) details.open = true;
    return target;
  };

  document.addEventListener("click", function (e) {
    var link = e.target.closest('a[href*="#"]');
    if (link && link.pathname === location.pathname) {
      openFromHash(link.hash);
      closeMenu();
      closeMega();
    }
  });
  window.addEventListener("hashchange", function () { openFromHash(location.hash); });
  if (location.hash) {
    var landed = openFromHash(location.hash);
    if (landed) landed.scrollIntoView();
  }
})();
