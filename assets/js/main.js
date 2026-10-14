/* =========================================================
   CRM — Comercial de Recambios Montemayor
   Interacciones de la web: menú, galerías, mapa y sub-navegación
   ========================================================= */

(function () {
  "use strict";

  /* ---------- Año actual en el pie ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- Cabecera: sombra al hacer scroll ---------- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Menú móvil ---------- */
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    document.body.classList.remove("nav-open");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  });

  /* ---------- Lightbox para galerías ----------
     Cualquier enlace con [data-gallery="nombre"] abre la imagen ampliada.
     Los enlaces con el mismo nombre forman una galería navegable. */
  var links = document.querySelectorAll("a[data-gallery]");
  if (links.length && typeof HTMLDialogElement === "function") {
    var dialog = document.createElement("dialog");
    dialog.className = "lightbox";
    dialog.setAttribute("aria-label", "Imagen ampliada");
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
      var link = items[index];
      var thumb = link.querySelector("img");
      img.src = link.href;
      img.alt = thumb ? thumb.alt : "";
      count.textContent = items.length > 1 ? index + 1 + " / " + items.length : "";
      prev.hidden = next.hidden = items.length < 2;
    };

    links.forEach(function (link) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        var name = link.getAttribute("data-gallery");
        items = Array.prototype.slice.call(document.querySelectorAll('a[data-gallery="' + name + '"]'));
        show(items.indexOf(link));
        dialog.showModal();
      });
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

    // Deslizar en móvil
    var startX = null;
    dialog.addEventListener("touchstart", function (e) { startX = e.touches[0].clientX; }, { passive: true });
    dialog.addEventListener("touchend", function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
      startX = null;
    });
  }

  /* ---------- Mapa: se carga solo al pulsar (sin cookies de terceros hasta entonces) ---------- */
  document.querySelectorAll("[data-map-src]").forEach(function (map) {
    var btn = map.querySelector("button");
    btn.addEventListener("click", function () {
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
     Si un enlace (#tacos, chips de la sub-navegación, URLs antiguas
     redirigidas…) apunta a un <details> cerrado, se abre antes de saltar. */
  var openFromHash = function (hash) {
    if (!hash || hash.length < 2) return;
    var target = document.getElementById(decodeURIComponent(hash.slice(1)));
    var details = target && target.closest("details");
    if (details && !details.open) details.open = true;
  };

  document.addEventListener("click", function (e) {
    var link = e.target.closest('a[href*="#"]');
    if (link && link.pathname === location.pathname) openFromHash(link.hash);
  });
  window.addEventListener("hashchange", function () { openFromHash(location.hash); });
  if (location.hash) {
    openFromHash(location.hash);
    var landed = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (landed) landed.scrollIntoView();
  }

  /* ---------- Sub-navegación: resalta la sección visible ---------- */
  var subnav = document.querySelector(".subnav");
  if (subnav && "IntersectionObserver" in window) {
    var chips = subnav.querySelectorAll("a");
    var byId = {};
    chips.forEach(function (a) { byId[a.hash.slice(1)] = a; });
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          chips.forEach(function (a) { a.classList.remove("is-active"); });
          var chip = byId[entry.target.id];
          if (chip) {
            chip.classList.add("is-active");
            var list = chip.closest("ul");
            var delta = chip.getBoundingClientRect().left - list.getBoundingClientRect().left;
            list.scrollTo({ left: list.scrollLeft + delta - list.clientWidth / 2 + chip.offsetWidth / 2, behavior: "smooth" });
          }
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    Object.keys(byId).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) observer.observe(el);
    });
  }
})();
