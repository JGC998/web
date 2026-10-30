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

  /* ---------- Carrusel de fotos de cada familia ----------
     <div data-carousel>
       <div class="carousel__track"> <a class="carousel__slide">…</a> … </div>
       <button data-carousel-prev> <div class="carousel__dots"> <button data-carousel-next>
     </div>
     Pasa solo cada 4,5 s mientras está a la vista; se detiene al tocarlo,
     al pasar el ratón por encima o si el sistema pide reducir animaciones. */
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll("[data-carousel]").forEach(function (carousel) {
    var track = carousel.querySelector(".carousel__track");
    var slides = Array.prototype.slice.call(track.children);
    var dotsBox = carousel.querySelector(".carousel__dots");
    if (slides.length < 2) return;

    var current = 0;
    var timer = null;
    var visible = false;
    var paused = false;
    var stopped = false; // el usuario ha interactuado: ya no pasa solo

    var dots = slides.map(function (_, i) {
      var dot = document.createElement("button");
      dot.type = "button";
      dot.className = "carousel__dot";
      dot.tabIndex = -1;
      dot.addEventListener("click", function () { stop(); goTo(i); });
      dotsBox.appendChild(dot);
      return dot;
    });
    if (slides.length > 8) dotsBox.classList.add("carousel__dots--many");

    var mark = function (i) {
      current = i;
      dots.forEach(function (d, k) { d.classList.toggle("is-active", k === i); });
    };

    var goTo = function (i) {
      i = (i + slides.length) % slides.length;
      var delta = slides[i].getBoundingClientRect().left - track.getBoundingClientRect().left;
      track.scrollTo({ left: track.scrollLeft + delta, behavior: reduceMotion ? "auto" : "smooth" });
      mark(i);
    };

    // Al deslizar con el dedo, actualizar el punto activo
    var scrollTimer = null;
    track.addEventListener("scroll", function () {
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(function () {
        var width = slides[0].getBoundingClientRect().width || 1;
        mark(Math.round(track.scrollLeft / (width + 12)));
      }, 80);
    }, { passive: true });

    var tick = function () {
      clearInterval(timer);
      timer = null;
      var open = !carousel.closest("details") || carousel.closest("details").open;
      if (!reduceMotion && !stopped && !paused && visible && open) {
        timer = setInterval(function () { goTo(current + 1); }, 4500);
      }
    };

    var stop = function () { stopped = true; tick(); };

    carousel.querySelector("[data-carousel-prev]").addEventListener("click", function () { stop(); goTo(current - 1); });
    carousel.querySelector("[data-carousel-next]").addEventListener("click", function () { stop(); goTo(current + 1); });
    track.addEventListener("pointerdown", stop);
    carousel.addEventListener("mouseenter", function () { paused = true; tick(); });
    carousel.addEventListener("mouseleave", function () { paused = false; tick(); });
    carousel.addEventListener("focusin", function () { paused = true; tick(); });
    carousel.addEventListener("focusout", function () { paused = false; tick(); });

    var details = carousel.closest("details");
    if (details) details.addEventListener("toggle", tick);

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        tick();
      }, { threshold: 0.3 }).observe(carousel);
    } else {
      visible = true;
    }

    mark(0);
    tick();
  });

  /* ---------- Vídeos de fondo ----------
     <video data-bg-video poster="foto.jpg"><source data-src="video.mp4"></video>
     Solo se descargan si el usuario no pide reducir animaciones ni ahorrar
     datos; si no, queda la imagen fija. Se pausan fuera de la pantalla. */
  var saveData = navigator.connection && navigator.connection.saveData;
  if (!reduceMotion && !saveData && "IntersectionObserver" in window) {
    document.querySelectorAll("video[data-bg-video]").forEach(function (video) {
      var loaded = false;
      new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
          if (!loaded) {
            video.querySelectorAll("source[data-src]").forEach(function (source) {
              source.src = source.getAttribute("data-src");
            });
            video.load();
            loaded = true;
          }
          var playing = video.play();
          if (playing && playing.catch) playing.catch(function () {});
        } else if (loaded) {
          video.pause();
        }
      }, { rootMargin: "200px 0px" }).observe(video);
    });
  }

  /* ---------- Formulario de presupuesto ----------
     - Marca el producto que llega en la URL (?producto=Faldetas · Goma)
     - Reduce las fotos en el propio móvil (máx. 1600 px) antes de enviarlas
     - Envía sin recargar y muestra el resultado; sin JS, el formulario
       funciona igual con un envío normal */
  var quote = document.querySelector("[data-quote]");
  if (quote) {
    var status = quote.querySelector(".quote__status");
    var boton = quote.querySelector("button[type=submit]");
    quote.querySelector("[name=t]").value = Date.now();

    var pedido = new URLSearchParams(location.search).get("producto");
    var select = quote.querySelector("[data-quote-producto]");
    if (pedido && select) {
      Array.prototype.forEach.call(select.options, function (op) {
        if (op.text === pedido) select.value = op.value || op.text;
      });
    }
    if (new URLSearchParams(location.search).get("error")) {
      status.textContent = "No se ha podido enviar. Revisa los datos o llámanos.";
      status.className = "quote__status is-error";
    }

    var reducir = function (archivo) {
      if (!window.createImageBitmap || !/^image\//.test(archivo.type)) return Promise.resolve(archivo);
      return createImageBitmap(archivo).then(function (bmp) {
        var escala = Math.min(1, 1600 / Math.max(bmp.width, bmp.height));
        var canvas = document.createElement("canvas");
        canvas.width = Math.round(bmp.width * escala);
        canvas.height = Math.round(bmp.height * escala);
        canvas.getContext("2d").drawImage(bmp, 0, 0, canvas.width, canvas.height);
        return new Promise(function (ok) {
          canvas.toBlob(function (blob) { ok(blob || archivo); }, "image/jpeg", 0.82);
        });
      }).catch(function () { return archivo; });
    };

    var aviso = function (texto, error) {
      status.textContent = texto;
      status.className = "quote__status" + (error ? " is-error" : " is-ok");
    };

    quote.addEventListener("submit", function (e) {
      if (!window.fetch || !window.FormData) return; // envío normal
      e.preventDefault();
      var nombre = quote.querySelector("[name=nombre]");
      var tel = quote.querySelector("[name=telefono]");
      var priv = quote.querySelector("[name=privacidad]");
      if (!nombre.value.trim()) { aviso("Escribe tu nombre.", true); nombre.focus(); return; }
      if (!tel.value.trim()) { aviso("Escribe un teléfono para poder contestarte.", true); tel.focus(); return; }
      if (!priv.checked) { aviso("Marca la casilla de la política de privacidad.", true); priv.focus(); return; }

      var datos = new FormData(quote);
      var fotos = Array.prototype.slice.call(quote.querySelector("[data-quote-fotos]").files || [], 0, 4);
      datos.delete("fotos");
      boton.disabled = true;
      aviso(fotos.length ? "Preparando las fotos…" : "Enviando…");

      Promise.all(fotos.map(reducir))
        .then(function (reducidas) {
          reducidas.forEach(function (blob, i) { datos.append("fotos", blob, "foto-" + (i + 1) + ".jpg"); });
          aviso("Enviando…");
          return fetch(quote.action, { method: "POST", body: datos, headers: { Accept: "application/json" } });
        })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res.ok) {
            location.href = "/presupuesto/gracias/";
          } else {
            aviso(res.mensaje || "No se ha podido enviar.", true);
            boton.disabled = false;
          }
        })
        .catch(function () {
          aviso("No se ha podido enviar. Revisa tu conexión o llámanos al 957 682 819.", true);
          boton.disabled = false;
        });
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

/* Campaña de temporada de la portada: se muestra la última que ha empezado según la fecha
   (data-campana="mes-día"). La página llega ya con la campaña del día en que se publicó;
   esto la corrige si desde entonces ha empezado otra. ?campana=03-15 permite probar una fecha. */
(function () {
  var avisos = document.querySelectorAll(".season[data-campana]");
  if (!avisos.length) return;
  var prueba = /[?&]campana=(\d\d-\d\d)/.exec(location.search);
  var d = new Date();
  var hoy = prueba ? prueba[1] : ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
  var lista = Array.prototype.slice.call(avisos).sort(function (a, b) {
    return a.dataset.campana < b.dataset.campana ? -1 : 1;
  });
  var empezadas = lista.filter(function (a) { return a.dataset.campana <= hoy; });
  var vigente = (empezadas.length ? empezadas : lista)[(empezadas.length ? empezadas : lista).length - 1];
  lista.forEach(function (a) { a.hidden = a !== vigente; });
})();
