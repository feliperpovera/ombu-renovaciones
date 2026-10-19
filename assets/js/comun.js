/* OMBU Renovaciones · Partes comunes a todas las páginas del sitio:
   encabezado, desplegable de Servicios, menú móvil, revelado, carriles, WhatsApp flotante y cookies. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var body = document.body;
  var ROOT = body.dataset.root || '../';          // ruta hasta la carpeta que contiene assets/

  /* ---------- Encabezado ---------- */
  var hdr = $('#hdr');
  var hero = $('.hero');
  function onScroll() {
    var solid = !hero || window.scrollY > hero.offsetHeight - 90;
    hdr.dataset.state = solid ? 'solid' : 'top';
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Desplegable de Servicios (escritorio) ---------- */
  var dropBtn = $('.hdr__drop-btn');
  var drop = $('#drop-servicios');
  if (dropBtn && drop) {
    var hoverT;
    var setDrop = function (open) {
      dropBtn.setAttribute('aria-expanded', String(open));
      if (open) { drop.hidden = false; requestAnimationFrame(function () { drop.classList.add('is-open'); }); }
      else { drop.classList.remove('is-open'); drop.hidden = true; }
    };
    dropBtn.addEventListener('click', function () { setDrop(dropBtn.getAttribute('aria-expanded') !== 'true'); });
    var li = dropBtn.parentElement;
    if (window.matchMedia('(hover: hover)').matches) {
      li.addEventListener('mouseenter', function () { clearTimeout(hoverT); setDrop(true); });
      li.addEventListener('mouseleave', function () { hoverT = setTimeout(function () { setDrop(false); }, 180); });
    }
    li.addEventListener('focusout', function (e) { if (!li.contains(e.relatedTarget)) setDrop(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && dropBtn.getAttribute('aria-expanded') === 'true') { setDrop(false); dropBtn.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (!li.contains(e.target)) setDrop(false);
      else if (e.target.closest('.drop a')) setDrop(false);
    });
  }

  /* ---------- Menú móvil ---------- */
  var burger = $('#burger');
  var menu = $('#menu');
  function setMenu(open) {
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    body.classList.toggle('menu-open', open);
    if (open) {
      menu.hidden = false;
      requestAnimationFrame(function () { menu.classList.add('is-open'); });
      var first = $('button, a', menu); if (first) first.focus({ preventScroll: true });
    } else {
      menu.classList.remove('is-open');
      setTimeout(function () { if (!menu.classList.contains('is-open')) menu.hidden = true; }, 350);
    }
  }
  burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true'); });
  menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') { setMenu(false); burger.focus(); }
  });
  window.matchMedia('(min-width: 960px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });

  var acc = $('.menu__acc');
  var sub = $('#menu-servicios');
  if (acc && sub) {
    acc.addEventListener('click', function () {
      var open = acc.getAttribute('aria-expanded') !== 'true';
      acc.setAttribute('aria-expanded', String(open));
      sub.hidden = !open;
    });
  }

  /* ---------- Revelado al hacer scroll ---------- */
  var reveals = $$('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); ro.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { ro.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- Carriles horizontales (scroll-snap nativo) ---------- */
  function initRail(scope) {
    var track = $('.rail__track', scope);
    if (!track || track._rail) return;
    track._rail = true;
    var bar = $('.rail__progress span', scope);
    var prev = $('[data-rail-prev]', scope);
    var next = $('[data-rail-next]', scope);
    function update() {
      var max = track.scrollWidth - track.clientWidth;
      var ratio = max > 0 ? track.clientWidth / track.scrollWidth : 1;
      var p = max > 0 ? track.scrollLeft / max : 0;
      if (bar) { bar.style.width = (ratio * 100) + '%'; bar.style.marginLeft = (p * (1 - ratio) * 100) + '%'; }
      if (prev) prev.disabled = track.scrollLeft < 4;
      if (next) next.disabled = track.scrollLeft > max - 4;
    }
    function page(dir) {
      var item = track.firstElementChild;
      var w = item ? item.getBoundingClientRect().width + parseFloat(getComputedStyle(track).columnGap || 16) : track.clientWidth;
      var n = Math.max(1, Math.floor(track.clientWidth / w));
      track.scrollBy({ left: dir * w * n, behavior: reduceMotion ? 'auto' : 'smooth' });
    }
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    if (prev) prev.addEventListener('click', function () { page(-1); });
    if (next) next.addEventListener('click', function () { page(1); });
    track.addEventListener('keydown', function (e) {
      if (e.target !== track) return;
      if (e.key === 'ArrowRight') { e.preventDefault(); page(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); page(-1); }
    });
    scope._railUpdate = update;
    update();
  }
  window.OMBU = { initRail: initRail, reduceMotion: reduceMotion };
  $$('[data-rail]').forEach(function (r) { initRail(r.closest('section') || r); });

  /* ---------- WhatsApp flotante ---------- */
  var fab = $('#fab');
  if (fab) {
    var contact = $('#contacto');
    if ('IntersectionObserver' in window) {
      var heroVisible = !!hero, contactVisible = false;
      var fabUpdate = function () {
        var past = hero ? !heroVisible : window.scrollY > 300;
        fab.classList.toggle('is-on', past && !contactVisible);
      };
      if (hero) new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; fabUpdate(); }, { threshold: 0.25 }).observe(hero);
      else window.addEventListener('scroll', fabUpdate, { passive: true });
      if (contact) new IntersectionObserver(function (e) { contactVisible = e[0].isIntersecting; fabUpdate(); }, { threshold: 0.1 }).observe(contact);
      fabUpdate();
    } else { fab.classList.add('is-on'); }
  }

  /* ---------- Aviso y preferencias de cookies ----------
     La elección queda en localStorage ('ombu-cookies'). Para cargar analítica o
     marketing en el futuro: leer OMBU.consent o escuchar el evento 'ombu:consent'. */
  var CK = 'ombu-cookies';
  var POLITICA = ROOT + 'sitio/legal/politica-de-datos.html';
  function leer() { try { return JSON.parse(localStorage.getItem(CK)); } catch (e) { return null; } }
  function guardar(analitica, marketing) {
    var c = { analitica: analitica, marketing: marketing, fecha: new Date().toISOString() };
    try { localStorage.setItem(CK, JSON.stringify(c)); } catch (e) { /* modo privado: solo esta visita */ }
    window.OMBU.consent = c;
    document.dispatchEvent(new CustomEvent('ombu:consent', { detail: c }));
    cerrarAviso();
    if (dlg.open) dlg.close();
  }
  window.OMBU.consent = leer();

  var aviso = document.createElement('section');
  aviso.className = 'ck on-dark';
  aviso.setAttribute('aria-label', 'Aviso de cookies');
  aviso.innerHTML =
    '<p class="ck__text">Usamos cookies necesarias para que el sitio funcione. Con tu permiso usaríamos también cookies de analítica y marketing. <a href="' + POLITICA + '#cookies">Más información</a></p>' +
    '<div class="ck__btns">' +
      '<button class="btn btn--light" type="button" data-ck="todas">Aceptar todas</button>' +
      '<button class="btn btn--light" type="button" data-ck="rechazar">Solo necesarias</button>' +
      '<button class="btn btn--ghost" type="button" data-ck="config">Configurar</button>' +
    '</div>';

  var dlg = document.createElement('dialog');
  dlg.className = 'ckd';
  dlg.setAttribute('aria-labelledby', 'ckd-title');
  function fila(id, titulo, texto, fija) {
    return '<label class="ckd__row"><span><strong>' + titulo + '</strong>' + texto + '</span>' +
      '<input class="switch" type="checkbox" id="ck-' + id + '"' + (fija ? ' checked disabled' : '') + '></label>';
  }
  dlg.innerHTML =
    '<form method="dialog" class="ckd__in">' +
      '<h2 class="ckd__title" id="ckd-title">Preferencias de cookies</h2>' +
      '<p class="ckd__lead">Elige qué cookies aceptas. Puedes cambiarlo cuando quieras desde el pie de página. <a href="' + POLITICA + '#cookies">Política de datos</a></p>' +
      fila('necesarias', 'Necesarias', 'Hacen funcionar el sitio y guardan esta elección. Siempre activas.', true) +
      fila('analitica', 'Analítica', 'Nos dicen qué páginas se visitan para mejorar el sitio.') +
      fila('marketing', 'Marketing', 'Permiten mostrarte anuncios de OMBU en otras plataformas.') +
      '<div class="ckd__btns">' +
        '<button class="btn" type="button" data-ck="guardar">Guardar preferencias</button>' +
        '<button class="btn btn--ghost" type="button" data-ck="todas">Aceptar todas</button>' +
      '</div>' +
      '<button class="ckd__x icon-btn" type="submit" aria-label="Cerrar">×</button>' +
    '</form>';

  function abrirAviso() { body.appendChild(aviso); body.classList.add('ck-open'); }
  function cerrarAviso() { if (aviso.parentNode) aviso.remove(); body.classList.remove('ck-open'); }
  function abrirPreferencias() {
    var c = window.OMBU.consent || {};
    $('#ck-analitica', dlg).checked = !!c.analitica;
    $('#ck-marketing', dlg).checked = !!c.marketing;
    if (!dlg.parentNode) body.appendChild(dlg);
    dlg.showModal();
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-ck], [data-cookies]');
    if (!b) return;
    var a = b.dataset.ck;
    if (b.hasAttribute('data-cookies') || a === 'config') abrirPreferencias();
    else if (a === 'todas') guardar(true, true);
    else if (a === 'rechazar') guardar(false, false);
    else if (a === 'guardar') guardar($('#ck-analitica', dlg).checked, $('#ck-marketing', dlg).checked);
  });
  if (!window.OMBU.consent) abrirAviso();
})();
