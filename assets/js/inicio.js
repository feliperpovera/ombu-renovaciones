/* OMBU Renovaciones · Tarjetas de proyecto con comparador, fichas, visor, testimonios y formulario.
   Se carga en Inicio, Proyectos y Contacto; cada parte se activa solo si su HTML existe.
   Lo común a todas las páginas (encabezado, menú, carriles) está en comun.js. */
(function () {
  'use strict';

  var WA = '573105996809';
  var IMG = '../assets/img/proyectos/';
  var PROYECTOS = window.OMBU_PROYECTOS || [];
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  function waLink(text) { return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(text); }

  /* Pequeña oscilación del divisor para que se entienda que se desliza */
  function hint(setPos, dur, amp, delay) {
    if (reduceMotion) return function () {};
    var raf = null;
    setTimeout(function () {
      var t0 = null;
      var step = function (t) {
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / dur);
        setPos(50 + Math.sin(p * Math.PI * 2) * amp * (1 - p * 0.3));
        if (p < 1) raf = requestAnimationFrame(step); else { setPos(50); raf = null; }
      };
      raf = requestAnimationFrame(step);
    }, delay || 0);
    return function () { if (raf) cancelAnimationFrame(raf); raf = null; };
  }

  /* ---------- Proyectos: tarjetas con comparador ----------
     Cada <ul data-proj="slug,slug"> recibe las tarjetas de esos proyectos (assets/js/proyectos.js). */
  function src(p, f) { return IMG + p.slug + '/' + f[0]; }
  function srcset(p, ph) { return src(p, ph[0]) + ' ' + ph[0][1] + 'w, ' + src(p, ph[1]) + ' ' + ph[1][1] + 'w'; }
  var porSlug = {};
  PROYECTOS.forEach(function (p) { porSlug[p.slug] = p; });

  function tarjeta(p, lazy) {
    var a = p.par[0], d = p.par[1];
    var total = p.despues.length + p.antes.length;
    return '<li class="card">' +
      '<div class="cmp" style="--pos: 50%">' +
        '<img class="cmp__img" src="' + src(p, d) + '" width="' + d[1] + '" height="' + d[2] + '" loading="' + lazy + '" decoding="async"' +
        ' alt="' + p.nombre + ', después de la renovación">' +
        '<div class="cmp__clip"><img class="cmp__img" src="' + src(p, a) + '" width="' + a[1] + '" height="' + a[2] + '" loading="' + lazy + '" decoding="async"' +
        ' alt="' + p.nombre + ', antes de la renovación"></div>' +
        '<span class="cmp__tag cmp__tag--a" aria-hidden="true">Antes</span>' +
        '<span class="cmp__tag cmp__tag--d" aria-hidden="true">Después</span>' +
        '<div class="cmp__grab" aria-hidden="true"><span class="cmp__knob"><svg><use href="#i-chev-l"/></svg><svg><use href="#i-chev-r"/></svg></span></div>' +
        '<input class="cmp__range" type="range" min="0" max="100" value="50" aria-label="Comparar antes y después en ' + p.nombre + '">' +
      '</div>' +
      '<button class="card__btn" type="button" data-open="' + p.slug + '">' +
        '<span class="card__txt"><span class="card__name">' + p.nombre + '</span>' +
        '<span class="card__meta">' + total + ' fotos · Ver proyecto</span></span>' +
        '<span class="card__go" aria-hidden="true"><svg><use href="#i-arrow"/></svg></span>' +
      '</button></li>';
  }
  $$('[data-proj]').forEach(function (ul) {
    var enCarril = !!ul.closest('.rail');
    ul.insertAdjacentHTML('beforeend', ul.dataset.proj.split(',').map(function (slug, i) {
      return porSlug[slug] ? tarjeta(porSlug[slug], enCarril && i < 2 ? 'eager' : 'lazy') : '';
    }).join(''));
  });

  /* Cada comparador: el divisor se arrastra desde su tirador (con el dedo) o desde
     cualquier punto de la foto (con el mouse). Un toque sin arrastre abre el proyecto;
     deslizar el dedo fuera del tirador sigue moviendo el carrusel. */
  $$('[data-proj] .cmp').forEach(function (cmp) {
    var range = $('.cmp__range', cmp);
    var grab = $('.cmp__grab', cmp);
    var card = cmp.parentElement;
    var stopHint = function () {};
    var setPos = function (v) {
      v = Math.max(0, Math.min(100, v));
      cmp.style.setProperty('--pos', v + '%');
      range.value = Math.round(v);
      cmp.dataset.edge = v < 14 ? 'left' : v > 86 ? 'right' : '';
    };
    var fromEvent = function (e) {
      var r = cmp.getBoundingClientRect();
      setPos(((e.clientX - r.left) / r.width) * 100);
    };
    range.addEventListener('input', function () { stopHint(); setPos(+range.value); });

    var drag = null;
    cmp.addEventListener('pointerdown', function (e) {
      var onGrab = grab.contains(e.target);
      drag = { x: e.clientX, y: e.clientY, t: Date.now(), active: onGrab || e.pointerType === 'mouse', moved: false };
      if (drag.active) { try { cmp.setPointerCapture(e.pointerId); } catch (err) {} stopHint(); cmp.classList.add('is-dragging'); if (onGrab) fromEvent(e); }
    });
    cmp.addEventListener('pointermove', function (e) {
      if (!drag) return;
      if (Math.abs(e.clientX - drag.x) > 5 || Math.abs(e.clientY - drag.y) > 5) drag.moved = true;
      if (drag.active && drag.moved) fromEvent(e);
    });
    cmp.addEventListener('pointerup', function () {
      if (drag && !drag.moved && Date.now() - drag.t < 450) $('[data-open]', card).click();
      drag = null; cmp.classList.remove('is-dragging');
    });
    cmp.addEventListener('pointercancel', function () { drag = null; cmp.classList.remove('is-dragging'); });
    cmp.addEventListener('dragstart', function (e) { e.preventDefault(); });

    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        if (!entries[0].isIntersecting) return;
        io.disconnect();
        stopHint = hint(setPos, 1600, 16, 200);
      }, { threshold: 0.7 });
      io.observe(cmp);
    }
  });
  $$('[data-proj]').forEach(function (ul) {
    var sec = ul.closest('section');
    if (sec && sec._railUpdate) sec._railUpdate();
  });

  /* ---------- Testimonios largos: plegables ---------- */
  $$('.quote__text').forEach(function (t, i) {
    if (t.scrollHeight <= t.clientHeight + 4) return;
    t.id = t.id || 'q-text-' + i;
    var more = document.createElement('button');
    more.type = 'button';
    more.className = 'quote__more';
    more.setAttribute('aria-expanded', 'false');
    more.setAttribute('aria-controls', t.id);
    more.textContent = 'Leer completo';
    more.addEventListener('click', function () {
      var open = more.getAttribute('aria-expanded') !== 'true';
      more.setAttribute('aria-expanded', String(open));
      t.classList.toggle('is-open', open);
      more.textContent = open ? 'Leer menos' : 'Leer completo';
      var tq = $('#testimonios'); if (tq._railUpdate) tq._railUpdate();
    });
    t.insertAdjacentElement('afterend', more);
  });

  /* ---------- Ficha de proyecto y visor (solo donde hay tarjetas) ---------- */
  var sheet = $('#sheet');
  if (sheet) {
    /* ---------- Diálogos con animación de salida ---------- */
    function closeAnimated(dlg, done) {
      if (!dlg.open) return;
      if (reduceMotion) { dlg.close(); if (done) done(); return; }
      dlg.classList.add('is-closing');
      setTimeout(function () {
        dlg.classList.remove('is-closing'); dlg.close(); if (done) done();
      }, 280);
    }

    /* ---------- Ficha de proyecto ---------- */
    var scroller = $('.sheet__scroll', sheet);
    var gal = $('#panel-gal');
    var tabs = $$('.tab', sheet);
    var current = null;
    var currentTab = 'despues';
    var lastFocus = null;

    function renderGallery(kind) {
      currentTab = kind;
      var list = current[kind];
      tabs.forEach(function (t) {
        var on = t.dataset.tab === kind;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
      });
      gal.setAttribute('aria-labelledby', kind === 'despues' ? 'tab-d' : 'tab-a');
      gal.innerHTML = list.map(function (ph, i) {
        return '<figure class="gal__item"><button class="gal__btn" type="button" data-lb="' + i + '" aria-label="Ampliar foto ' + (i + 1) + ' de ' + list.length + ' (' + (kind === 'despues' ? 'después' : 'antes') + ')">' +
          '<img src="' + src(current, ph[0]) + '" width="' + ph[0][1] + '" height="' + ph[0][2] + '" loading="lazy" decoding="async" alt="">' +
          '</button></figure>';
      }).join('');
    }

    function openSheet(slug, push) {
      var p = PROYECTOS.filter(function (x) { return x.slug === slug; })[0];
      if (!p) return;
      current = p;
      lastFocus = lastFocus || document.activeElement;
      var cover = p.despues[0];
      var img = $('#sheet-cover');
      img.src = src(p, cover[1]); img.srcset = srcset(p, cover); img.sizes = '(min-width: 960px) 1040px, 100vw';
      img.width = cover[1][1]; img.height = cover[1][2];
      img.alt = 'Proyecto ' + p.nombre + ' terminado';
      $('#sheet-title').textContent = p.nombre;
      $('.sheet__bar-title', sheet).textContent = p.nombre;
      var meta = p.despues.length + ' fotos del resultado';
      if (p.antes.length) meta += ' · ' + p.antes.length + ' del estado inicial';
      $('#sheet-meta').textContent = meta;
      $('span', tabs[0]).textContent = '(' + p.despues.length + ')';
      $('span', tabs[1]).textContent = '(' + p.antes.length + ')';
      tabs[1].disabled = !p.antes.length;
      $('#sheet-wa').href = waLink('Hola OMBU, vi el proyecto ' + p.nombre + ' en su página y quiero algo así para mi espacio.');
      renderGallery('despues');
      scroller.scrollTop = 0;
      sheet.classList.remove('is-scrolled');
      if (!sheet.open) sheet.showModal();
      document.body.classList.add('sheet-open');
      $('[data-close]', sheet).focus({ preventScroll: true });
      if (push) history.pushState({ sheet: slug }, '', '#proyecto/' + slug);
    }

    function hideSheet() {
      closeAnimated(sheet, function () {
        document.body.classList.remove('sheet-open');
        if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
        lastFocus = null;
      });
    }
    function requestCloseSheet() {
      if (history.state && history.state.sheet) history.back(); // popstate cierra
      else { hideSheet(); if (location.hash.indexOf('#proyecto/') === 0) history.replaceState(null, '', location.pathname + location.search); }
    }

    document.addEventListener('click', function (e) {
      var b = e.target.closest('[data-open]');
      if (b) { e.preventDefault(); lastFocus = b.closest('.menu, .drop') ? null : b; openSheet(b.dataset.open, true); }
    });
    $('[data-close]', sheet).addEventListener('click', requestCloseSheet);
    sheet.addEventListener('cancel', function (e) { e.preventDefault(); requestCloseSheet(); });
    sheet.addEventListener('click', function (e) { if (e.target === sheet) requestCloseSheet(); });
    scroller.addEventListener('scroll', function () {
      sheet.classList.toggle('is-scrolled', scroller.scrollTop > $('.sheet__hero', sheet).offsetHeight - 70);
    }, { passive: true });

    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () {
        if (t.dataset.tab === currentTab) return;
        gal.classList.add('is-swapping');
        setTimeout(function () { renderGallery(t.dataset.tab); gal.classList.remove('is-swapping'); }, 150);
      });
      t.addEventListener('keydown', function (e) {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        var other = tabs[1 - i];
        if (other.disabled) return;
        other.focus(); other.click();
      });
    });

    $('[data-share]', sheet).addEventListener('click', function () {
      var url = location.href.split('#')[0] + '#proyecto/' + current.slug;
      var data = { title: current.nombre + ' · OMBU Renovaciones', text: 'Mira este proyecto de OMBU Renovaciones', url: url };
      if (navigator.share) { navigator.share(data).catch(function () {}); return; }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          var btn = $('[data-share]', sheet);
          btn.setAttribute('aria-label', 'Enlace copiado');
          btn.classList.add('is-done');
          setTimeout(function () { btn.setAttribute('aria-label', 'Compartir proyecto'); btn.classList.remove('is-done'); }, 1800);
        });
      }
    });

    window.addEventListener('popstate', function () {
      var m = location.hash.match(/^#proyecto\/([\w-]+)/);
      if (m) openSheet(m[1], false);
      else if (sheet.open) { if (lb.open) lb.close(); hideSheet(); }
    });

    /* ---------- Visor de fotos ---------- */
    var lb = $('#lb');
    var lbTrack = $('#lb-track');
    var lbCount = $('#lb-count');
    var lbList = [];
    var lbIndex = 0;

    function lbGo(i, smooth) {
      lbIndex = Math.max(0, Math.min(lbList.length - 1, i));
      lbTrack.scrollTo({ left: lbIndex * lbTrack.clientWidth, behavior: smooth && !reduceMotion ? 'smooth' : 'auto' });
      lbUpdate();
    }
    function lbUpdate() {
      lbCount.textContent = (lbIndex + 1) + ' / ' + lbList.length + ' · ' + (currentTab === 'despues' ? 'Después' : 'Antes');
      $('[data-lb-prev]', lb).disabled = lbIndex === 0;
      $('[data-lb-next]', lb).disabled = lbIndex === lbList.length - 1;
    }
    gal.addEventListener('click', function (e) {
      var b = e.target.closest('[data-lb]');
      if (!b) return;
      lbList = current[currentTab];
      lbTrack.innerHTML = lbList.map(function (ph, i) {
        return '<li><img src="' + src(current, ph[1]) + '" width="' + ph[1][1] + '" height="' + ph[1][2] + '"' +
          ' loading="' + (Math.abs(i - +b.dataset.lb) < 2 ? 'eager' : 'lazy') + '" decoding="async"' +
          ' alt="' + current.nombre + ', foto ' + (i + 1) + ' (' + (currentTab === 'despues' ? 'después' : 'antes') + ')"></li>';
      }).join('');
      lb.showModal();
      requestAnimationFrame(function () { lbGo(+b.dataset.lb, false); });
      lb._opener = b;
    });
    var lbScrollT;
    lbTrack.addEventListener('scroll', function () {
      clearTimeout(lbScrollT);
      lbScrollT = setTimeout(function () {
        var i = Math.round(lbTrack.scrollLeft / lbTrack.clientWidth);
        if (i !== lbIndex) { lbIndex = i; lbUpdate(); }
      }, 60);
    }, { passive: true });
    $('[data-lb-prev]', lb).addEventListener('click', function () { lbGo(lbIndex - 1, true); });
    $('[data-lb-next]', lb).addEventListener('click', function () { lbGo(lbIndex + 1, true); });
    $('[data-close]', lb).addEventListener('click', function () { lb.close(); });
    lb.addEventListener('close', function () { if (lb._opener) lb._opener.focus({ preventScroll: true }); });
    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); lbGo(lbIndex + 1, true); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); lbGo(lbIndex - 1, true); }
    });
    window.addEventListener('resize', function () { if (lb.open) lbGo(lbIndex, false); });

    /* Enlace directo a un proyecto (#proyecto/kuna-1002) */
    var initial = location.hash.match(/^#proyecto\/([\w-]+)/);
    if (initial) openSheet(initial[1], false);
  }

  /* ---------- Formulario de contacto → WhatsApp ---------- */
  var form = $('#form');
  if (form) {
    var servicio = new URLSearchParams(location.search).get('servicio');
    if (servicio) $('#f-msg').value = 'Me interesa el servicio de ' + servicio + '. ';
    var setError = function (input, msg) {
      var err = $('#' + input.getAttribute('aria-describedby'));
      input.setAttribute('aria-invalid', msg ? 'true' : 'false');
      err.textContent = msg || '';
    };
    var validate = function (input) {
      var v = input.value.trim();
      if (input.type === 'checkbox') return input.checked ? '' : 'Necesitamos tu autorización para contactarte.';
      if (input.name === 'nombre') return v.length < 2 ? 'Escribe tu nombre.' : '';
      if (input.name === 'apellido') return v.length < 2 ? 'Escribe tu apellido.' : '';
      if (input.name === 'ciudad') return v.length < 2 ? 'Escribe tu ciudad.' : '';
      if (input.name === 'celular') {
        var digits = v.replace(/\D/g, '');
        if (!digits) return 'Escribe tu número de celular.';
        if (digits.length < 7) return 'Revisa el número: parece incompleto.';
      }
      return '';
    };
    var campos = $$('input[required]', form);
    campos.forEach(function (input) {
      input.addEventListener(input.type === 'checkbox' ? 'change' : 'blur', function () {
        if (input.type === 'checkbox' || input.value) setError(input, validate(input));
      });
      input.addEventListener('input', function () { if (input.getAttribute('aria-invalid') === 'true') setError(input, validate(input)); });
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstBad = null;
      campos.forEach(function (input) {
        var msg = validate(input); setError(input, msg);
        if (msg && !firstBad) firstBad = input;
      });
      if (firstBad) { firstBad.focus(); return; }
      var d = new FormData(form);
      var t = function (k) { return String(d.get(k) || '').trim(); };
      var espacio = t('espacio');
      var text = 'Hola OMBU, soy ' + t('nombre') + ' ' + t('apellido') + ', de ' + t('ciudad') + '. Quiero transformar ' +
        (espacio === 'Otro' ? 'un espacio' : 'mi ' + espacio.toLowerCase()) + '.';
      if (t('mensaje')) text += '\n\nMi idea: ' + t('mensaje');
      text += '\n\nMi celular: ' + t('celular');
      text += '\n\nAutorizo el tratamiento de mis datos según su política de datos.';
      var url = waLink(text);
      window.open(url, '_blank', 'noopener');
      $('#form-wa').href = url;
      var ok = $('#form-ok');
      form.hidden = true; ok.hidden = false; ok.focus();
    });
  }
})();
