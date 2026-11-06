# -*- coding: utf-8 -*-
"""OMBU · construye el sitio completo en dist/ a partir de contenido/ (lo que edita el panel),
assets/ (CSS, JS, fuentes, marca) y panel/ (que queda en /admin).

    python3 herramientas/fotos.py && python3 herramientas/generar.py   (npm run construir)

No hay textos aquí: todo sale de contenido/. Lo que falta (fotos, datos legales) sale marcado
«pendiente»: no se inventa. Para volver editable algo nuevo: agregar el campo en panel/esquema.js,
en contenido/ y en la plantilla de este archivo.
"""
import glob
import html
import json
import os
import re
import shutil
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(RAIZ, "dist")
URL = "https://omburenovaciones.com/"
LEGALES = [
    ("terminos-y-condiciones", "Términos y condiciones"),
    ("politica-de-datos", "Política de datos"),
    ("aviso-de-privacidad", "Aviso de privacidad"),
    ("politica-de-cookies", "Política de cookies"),
]
ICONOS_ATRIBUTOS = ["i-shield", "i-design", "i-compare", "i-chat", "i-people"]
ICONOS_PASOS = ["i-chat", "i-plan", "i-build", "i-key"]
MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()


def leer(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        return json.load(f)


def carpeta(nombre):
    return [leer(os.path.relpath(f, RAIZ)) for f in sorted(glob.glob(os.path.join(RAIZ, "contenido", nombre, "*.json")))]


PAG = {os.path.basename(f)[:-5]: leer(os.path.relpath(f, RAIZ)) for f in glob.glob(os.path.join(RAIZ, "contenido/paginas/*.json"))}
GEN = PAG["general"]
SERVICIOS = sorted((s for s in carpeta("servicios") if s.get("publicado", True)), key=lambda s: s["orden"])
PROYECTOS = sorted((p for p in carpeta("proyectos") if p.get("publicado", True)), key=lambda p: p["orden"])
ARTICULOS = sorted((a for a in carpeta("blog") if a.get("publicado", True)), key=lambda a: a["fecha"], reverse=True)
try:
    MEDIDAS = leer("dist/fotos/medidas.json")
except FileNotFoundError:
    raise SystemExit("Falta dist/fotos/medidas.json: corre primero python3 herramientas/fotos.py")

C = GEN["contacto"]
WA = "https://wa.me/" + re.sub(r"\D", "", C["whatsapp"])
WA_COTIZAR = WA + "?text=" + quote(C["mensaje_whatsapp"])

ICONOS_EXTRA = """    <symbol id="i-chev-d" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></g></symbol>
    <symbol id="i-link" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/></g></symbol>
    <symbol id="i-sofa" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 11V8a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v3"/><path d="M3 13a2 2 0 1 1 4 0v2h10v-2a2 2 0 1 1 4 0v4H3z"/><path d="M6 17v2M18 17v2"/></g></symbol>
    <symbol id="i-clipboard" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="4.5" width="14" height="16.5" rx="2"/><path d="M9 3h6v3H9z"/><path d="M9 13l2 2 4-4"/></g></symbol>
    <symbol id="i-camera" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></g></symbol>"""


# ---------------------------------------------------------------- utilidades

def R(n):
    """Rutas para una página a n carpetas de la raíz del sitio (0 = raíz, 1 = blog/, servicios/, legal/)."""
    sube = "../" * n
    return {"A": sube + "assets/", "F": sube + "fotos/", "u": lambda p: sube + p, "root": sube or "./"}


def e(s):
    return html.escape(str(s or ""), quote=True)


def en_linea(t):
    """Formato sencillo dentro de un texto: **negrita**, *cursiva*, [texto](enlace), {pendiente}."""
    t = e(t).replace("&#x27;", "'")
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    t = re.sub(r"\{(.+?)\}", r'<mark class="pend">\1</mark>', t)

    def enlace(m):
        url = m[2].replace("&amp;", "&")
        afuera = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
        return f'<a href="{e(url)}"{afuera}>{m[1]}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", enlace, t)


def stem(f):
    return re.sub(r"\.[a-zA-Z]+$", "", (f or "").split("/")[-1])


def medida(f):
    s = stem(f)
    if s not in MEDIDAS:
        raise SystemExit(f"Foto sin procesar: {f}")
    return MEDIDAS[s][0], MEDIDAS[s][1]


def foto(f, n, alt="", sizes="(min-width: 960px) 560px, 100vw", lazy=True):
    F, s = R(n)["F"], stem(f)
    w, h = medida(f)
    carga = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    return (f'<img src="{F}{s}-800.webp" srcset="{F}{s}-800.webp {min(w, 800)}w, {F}{s}.webp {w}w" sizes="{sizes}" '
            f'width="{w}" height="{h}"{carga} alt="{e(alt)}">')


def md(texto, n, lead=False):
    """Formato del panel: ## subtítulo, ### subtítulo menor, - lista, > cita, ![descripción](foto "pie"),
    **negrita**, *cursiva*, [texto](enlace), {pendiente}. Dos fotos seguidas salen lado a lado."""
    salida = []
    for i, b in enumerate(x.strip() for x in re.split(r"\n{2,}", (texto or "").replace("\r", ""))):
        if not b:
            continue
        lineas = b.split("\n")
        fotos = [re.fullmatch(r'!\[(.*?)\]\((\S+?)(?: "(.*)")?\)', l.strip()) for l in lineas]
        if all(fotos):
            if len(fotos) == 2:
                caja = "".join(f"<div>{foto(m[2], n, m[1], '(min-width: 600px) 400px, 50vw')}<span>{e(m[3])}</span></div>" for m in fotos)
                salida.append(f'<figure class="prose__pair">{caja}</figure>')
            else:
                for m in fotos:
                    pie_ = f"<figcaption>{e(m[3])}</figcaption>" if m[3] else ""
                    salida.append(f'<figure class="prose__fig">{foto(m[2], n, m[1], "(min-width: 960px) 760px, 100vw")}{pie_}</figure>')
        elif b == "[[responsable]]":
            salida.append(responsable())
        elif b == "[[cookies]]":
            salida.append('<p><button class="btn" type="button" data-cookies>Preferencias de cookies</button></p>')
        elif b.startswith("### "):
            salida.append(f"<h3>{en_linea(b[4:])}</h3>")
        elif b.startswith("## "):
            salida.append(f"<h2{' id=\"cookies\"' if 'Cookies' in b else ''}>{en_linea(b[3:])}</h2>")
        elif b.startswith("> "):
            salida.append(f'<blockquote class="prose__quote">{en_linea(re.sub(r"^> ?", "", b, flags=re.M))}</blockquote>')
        elif re.match(r"[-*] ", b):
            salida.append("<ul>" + "".join(f"<li>{en_linea(l[2:])}</li>" for l in lineas) + "</ul>")
        else:
            clase = ' class="prose__lead"' if lead and not salida else ""
            salida.append(f"<p{clase}>{'<br>'.join(en_linea(l) for l in lineas)}</p>")
    return "\n".join(salida)


def responsable():
    L = GEN["legal"]
    p = lambda v: e(v) if v else '<mark class="pend">por confirmar</mark>'
    return f"""<ul>
  <li><strong>Responsable:</strong> {e(L['responsable'])}</li>
  <li><strong>NIT:</strong> {p(L['nit'])}</li>
  <li><strong>Domicilio:</strong> {e(C['ubicacion'])}, Colombia. Dirección: {p(L['direccion'])}</li>
  <li><strong>Correo:</strong> {p(L['correo'])}</li>
  <li><strong>WhatsApp:</strong> <a href="{WA}" target="_blank" rel="noopener">{e(C['whatsapp'])}</a></li>
</ul>"""


def fecha_larga(f):
    a, m, d = f.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {a}"


def ico(i):
    return f'<svg aria-hidden="true"><use href="#{i}"/></svg>'


def tit(o):
    return f'{e(o["titulo"])} <em>{e(o["titulo_em"])}</em>'


def sprite():
    with open(os.path.join(RAIZ, "herramientas", "iconos.svg.txt"), encoding="utf-8") as f:
        simbolos = f.read()
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">\n  <defs>\n'
            + simbolos + "\n" + ICONOS_EXTRA + "\n  </defs>\n</svg>")


def pendiente(texto, clase=""):
    return f'<div class="ph {clase}" role="img" aria-label="{e(texto)}">{ico("i-camera")}<span>{e(texto)}</span></div>'


# ---------------------------------------------------------------- partes comunes

MENU = [("inicio", "Inicio", "index.html"), ("nosotros", "Nosotros", "nosotros.html"), ("servicios", "Servicios", "servicios/index.html"),
        ("proyectos", "Proyectos", "proyectos.html"), ("blog", "Blog", "blog/index.html"), ("contacto", "Contacto", "contacto.html")]


def head(seo, n, og="website", extra=""):
    A = R(n)["A"]
    t, d = e(seo["titulo"]), e(seo["descripcion"])
    return f"""<!doctype html>
<html lang="es" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{t}</title>
  <meta name="description" content="{d}">
  <meta name="theme-color" content="#363840">
  <meta property="og:type" content="{og}">
  <meta property="og:locale" content="es_CO">
  <meta property="og:site_name" content="OMBU Renovaciones">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{d}">
  <meta property="og:image" content="{URL}assets/img/og-sitio.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="{A}img/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="{A}img/favicon-48.png" sizes="48x48" type="image/png">
  <link rel="apple-touch-icon" href="{A}img/apple-touch-icon.png">
  <link rel="preload" href="{A}fonts/poppins-900.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{A}fonts/poppins-300.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{A}css/brand.css">
  <link rel="stylesheet" href="{A}css/sitio.css">
  <link rel="stylesheet" href="{A}css/blog.css">
{extra}  <script>document.documentElement.classList.replace('no-js', 'js');</script>
</head>
"""


def redes():
    return f"""<a href="{e(C['instagram_url'])}" target="_blank" rel="noopener" aria-label="Instagram de OMBU">{ico("i-ig")}</a>
      <a href="{e(C['facebook_url'])}" target="_blank" rel="noopener" aria-label="Facebook de OMBU">{ico("i-fb")}</a>"""


def cabecera(n, activo):
    r = R(n)
    u = r["u"]
    cur = lambda k: ' aria-current="page"' if k == activo else ""
    svc_drop = "\n".join(
        f'              <li><a href="{u("servicios/" + s["url"] + ".html")}"{cur("svc-" + s["url"])}><span class="drop__ico">{ico(s["icono"])}</span>'
        f'<span><strong>{e(s["nombre"])}</strong>{e(s["resumen"])}</span></a></li>' for s in SERVICIOS)
    svc_menu = "\n".join(f'          <li><a href="{u("servicios/" + s["url"] + ".html")}">{e(s["nombre"])}</a></li>' for s in SERVICIOS)
    nav, menu = [], []
    for k, t, p in MENU:
        if k == "servicios":
            es = " is-current" if activo.startswith("svc") or activo == "servicios" else ""
            nav.append(f"""        <li class="has-drop">
          <button class="hdr__drop-btn{es}" type="button" aria-expanded="false" aria-controls="drop-servicios">Servicios <svg class="chev" aria-hidden="true"><use href="#i-chev-d"/></svg></button>
          <div class="drop" id="drop-servicios" hidden>
            <div class="drop__head">
              <p class="drop__title">Nuestros servicios</p>
              <a class="link-arrow" href="{u(p)}">Ver todos {ico("i-arrow")}</a>
            </div>
            <ul class="drop__grid drop__grid--svc" role="list">
{svc_drop}
            </ul>
          </div>
        </li>""")
            menu.append(f"""      <li>
        <button class="menu__acc" type="button" aria-expanded="false" aria-controls="menu-servicios">Servicios <svg class="chev" aria-hidden="true"><use href="#i-chev-d"/></svg></button>
        <ul class="menu__sub" id="menu-servicios" role="list" hidden>
{svc_menu}
          <li><a href="{u(p)}">Ver todos</a></li>
        </ul>
      </li>""")
        else:
            if k != "contacto":
                nav.append(f'        <li><a href="{u(p)}"{cur(k)}>{t}</a></li>')
            menu.append(f'      <li><a href="{u(p)}"{cur(k)}>{t}</a></li>')
    nl = "\n"
    return f"""<!-- ============ Encabezado ============ -->
<header class="hdr" id="hdr" data-state="{'top' if activo == 'inicio' else 'solid'}">
  <div class="hdr__in wrap">
    <a class="hdr__logo" href="{u('index.html')}" aria-label="OMBU Renovaciones, ir al inicio">
      <svg class="logo" viewBox="0 0 156 41" aria-hidden="true"><use href="{r['A']}img/marca.svg#ombu-logo"/></svg>
    </a>
    <nav class="hdr__nav" aria-label="Principal">
      <ul>
{nl.join(nav)}
      </ul>
    </nav>
    <a class="btn hdr__cta" href="{u('contacto.html')}"{cur('contacto')}>Contacto</a>
    <button class="hdr__burger" id="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Abrir menú">
      <span></span><span></span>
    </button>
  </div>
</header>

<!-- Menú móvil -->
<div class="menu on-dark" id="menu" hidden>
  <nav class="menu__nav" aria-label="Menú">
    <ul>
{nl.join(menu)}
    </ul>
  </nav>
  <div class="menu__foot">
    <a class="btn btn--light btn--lg btn--block" href="{e(WA_COTIZAR)}" target="_blank" rel="noopener">
      {ico("i-wa")} Escríbenos por WhatsApp
    </a>
    <div class="menu__social">
      {redes()}
    </div>
  </div>
</div>
"""


def pie(n):
    r = R(n)
    u = r["u"]
    P = GEN["pie"]
    links = "\n".join(f'        <li><a href="{u(p)}">{t}</a></li>' for k, t, p in MENU)
    legales = "".join(f'<a href="{u("legal/" + f + ".html")}">{t}</a>' for f, t in LEGALES)
    return f"""<!-- ============ Pie ============ -->
<footer class="ftr on-dark">
  <div class="wrap ftr__grid">
    <div class="ftr__brand">
      <svg class="logo" viewBox="0 0 156 41" role="img" aria-label="OMBU"><use href="{r['A']}img/marca.svg#ombu-logo"/></svg>
      <p>{e(P['frase'])} <em>{e(P['frase_em'])}</em></p>
    </div>
    <nav class="ftr__nav" aria-label="Pie de página">
      <ul>
{links}
      </ul>
    </nav>
    <div class="ftr__social">
      <p>Síguenos</p>
      <div>
      {redes()}
        <a href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp de OMBU">{ico("i-wa")}</a>
      </div>
    </div>
  </div>
  <div class="wrap ftr__bottom">
    <p>{e(P['derechos'])}</p>
    <p class="ftr__legal">{legales}<button type="button" data-cookies>Preferencias de cookies</button><a href="{u('admin/')}" rel="nofollow">Panel</a></p>
  </div>
</footer>
"""


def fab():
    return f"""<a class="fab" id="fab" href="{e(WA_COTIZAR)}" target="_blank" rel="noopener" aria-label="Escríbenos por WhatsApp">
  {ico("i-wa")}
</a>
"""


def dialogos():
    """Ficha de proyecto y visor de fotos (páginas con tarjetas de proyecto)."""
    return f"""
<!-- ============ Ficha de proyecto ============ -->
<dialog class="sheet" id="sheet" aria-labelledby="sheet-title">
  <div class="sheet__bar">
    <button class="icon-btn" type="button" data-close aria-label="Cerrar proyecto">{ico("i-arrow-l")}</button>
    <p class="sheet__bar-title" aria-hidden="true"></p>
    <button class="icon-btn sheet__share" type="button" data-share aria-label="Compartir proyecto"><svg aria-hidden="true" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 15V3M7 8l5-5 5 5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></g></svg></button>
  </div>
  <div class="sheet__scroll">
    <div class="sheet__hero"><img alt="" id="sheet-cover"></div>
    <div class="sheet__body">
      <p class="eyebrow">Proyecto OMBU</p>
      <h2 class="title sheet__title" id="sheet-title"></h2>
      <p class="sheet__meta" id="sheet-meta"></p>
      <div class="sheet__ficha" id="sheet-ficha"></div>
      <div class="tabs" role="tablist" aria-label="Fotos del proyecto">
        <button class="tab" role="tab" type="button" id="tab-d" aria-controls="panel-gal" aria-selected="true" data-tab="despues">Después <span></span></button>
        <button class="tab" role="tab" type="button" id="tab-a" aria-controls="panel-gal" aria-selected="false" data-tab="antes">Antes <span></span></button>
      </div>
      <div class="gal" id="panel-gal" role="tabpanel" aria-labelledby="tab-d"></div>
    </div>
  </div>
  <div class="sheet__cta">
    <a class="btn btn--lg btn--block" id="sheet-wa" href="#" target="_blank" rel="noopener">
      {ico("i-wa")} Quiero un proyecto así
    </a>
  </div>
</dialog>

<!-- ============ Visor de fotos ============ -->
<dialog class="lb" id="lb" aria-label="Visor de fotos">
  <div class="lb__top">
    <p class="lb__count" id="lb-count" aria-live="polite"></p>
    <button class="icon-btn icon-btn--dark" type="button" data-close aria-label="Cerrar visor">{ico("i-close")}</button>
  </div>
  <ul class="lb__track" id="lb-track" role="list"></ul>
  <button class="icon-btn icon-btn--dark lb__nav lb__nav--prev" type="button" data-lb-prev aria-label="Foto anterior">{ico("i-chev-l")}</button>
  <button class="icon-btn icon-btn--dark lb__nav lb__nav--next" type="button" data-lb-next aria-label="Foto siguiente">{ico("i-chev-r")}</button>
</dialog>
"""


def pagina(seo, n, activo, pagina_id, cuerpo, js=(), og="website", extra_head="", extra_body="", antes_js=""):
    A = R(n)["A"]
    scripts = "\n".join(f'<script src="{A}js/{j}"></script>' for j in ("proyectos.js", "comun.js") + tuple(js))
    return (head(seo, n, og, extra_head)
            + f'<body data-page="{pagina_id}" data-root="{R(n)["root"]}" data-wa="{re.sub(r"[^0-9]", "", C["whatsapp"])}">\n'
            + sprite() + '\n\n<a class="skip" href="#contenido">Saltar al contenido</a>\n\n' + cabecera(n, activo)
            + '\n<main id="contenido">\n' + cuerpo + '\n</main>\n\n' + pie(n) + fab() + extra_body
            + "\n" + antes_js + scripts + "\n</body>\n</html>\n")


def phero(o, migas, extra=""):
    """Encabezado de página interior. migas: [(texto, href|None)]"""
    m = '<span aria-hidden="true">/</span>'.join(
        f'<a href="{h}">{t}</a>' if h else f'<span aria-current="page">{t}</span>' for t, h in migas)
    return f"""  <section class="bhero" aria-labelledby="page-title">
    <div class="wrap">
      <nav class="crumbs" aria-label="Ruta">{m}</nav>
      <h1 class="display bhero__title" id="page-title">{tit(o)}</h1>
      <p class="lead">{en_linea(o['texto'])}</p>{extra}
    </div>
  </section>
"""


# ---------------------------------------------------------------- secciones reutilizables

def sec_servicios(n, o, boton="", ocultar=()):
    u = R(n)["u"]
    lista = [(i, s) for i, s in enumerate(SERVICIOS, 1) if s["url"] not in ocultar]
    if not lista:
        return ""
    cards = "\n".join(f"""        <li class="svc reveal">
          <a class="svc__link" href="{u('servicios/' + s['url'] + '.html')}">
            <span class="svc__top"><span class="svc__ico">{ico(s['icono'])}</span><span class="svc__n" aria-hidden="true">{i:02d}</span></span>
            <h3 class="svc__name">{e(s['nombre'])}</h3>
            <p>{e(s['resumen'])}</p>
            <span class="svc__more">Ver servicio {ico('i-arrow')}</span>
          </a>
        </li>""" for i, s in lista)
    pie_ = f'\n      <a class="btn btn--lg sec__cta" href="{u("servicios/index.html")}">{e(boton)} {ico("i-arrow")}</a>' if boton else ""
    return f"""  <section class="sec svcs" id="servicios" aria-labelledby="svc-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">{e(o['eyebrow'])}</p>
        <h2 class="title" id="svc-title">{tit(o)}</h2>
      </div>
      <ul class="svc__grid" role="list">
{cards}
      </ul>{pie_}
    </div>
  </section>
"""


def sec_por_que(n, o):
    cards = "\n".join(f"""        <li class="why__card reveal">
          <span class="why__ico">{ico(ICONOS_ATRIBUTOS[i % 5])}</span>
          <h3>{e(a['titulo'])}</h3>
          <p>{e(a['texto'])}</p>
        </li>""" for i, a in enumerate(GEN["atributos"]["lista"]))
    return f"""  <section class="sec why on-dark" id="por-que" aria-labelledby="why-title">
    <svg class="why__ring" viewBox="0 0 2250 2250" aria-hidden="true"><use href="{R(n)['A']}img/marca.svg#ombu-mark"/></svg>
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">{e(o['eyebrow'])}</p>
        <h2 class="title" id="why-title">{tit(o)}</h2>
      </div>
      <ul class="why__grid why__grid--5" role="list">
{cards}
      </ul>
    </div>
  </section>
"""


def sec_pasos(n):
    u = R(n)["u"]
    o = PAG["inicio"]["proceso"]
    pasos = "\n".join(f"""        <li class="step reveal">
          <span class="step__n" aria-hidden="true">{i + 1:02d}</span>
          <span class="step__ico">{ico(ICONOS_PASOS[i % 4])}</span>
          <h3>{e(p['titulo'])}</h3>
          <p>{e(p['texto'])}</p>
        </li>""" for i, p in enumerate(GEN["pasos"]["lista"]))
    return f"""  <section class="sec process" id="proceso" aria-labelledby="process-title">
    <div class="wrap process__grid">
      <div class="process__intro reveal">
        <p class="eyebrow">{e(o['eyebrow'])}</p>
        <h2 class="title" id="process-title">{tit(o)}</h2>
        <p class="lead">{e(o['texto'])}</p>
        <a class="btn btn--lg process__cta" href="{u('nosotros.html#proceso')}">{e(o['boton'])} {ico('i-arrow')}</a>
      </div>
      <ol class="steps" role="list">
{pasos}
      </ol>
    </div>
  </section>
"""


def carril(slugs, etiqueta):
    """Carrusel de tarjetas con comparador (las dibuja inicio.js a partir de data-proj)."""
    return f"""    <div class="rail" data-rail>
      <ul class="rail__track" data-proj="{','.join(slugs)}" role="list" tabindex="0" aria-label="{etiqueta}. Desliza para ver más."></ul>
    </div>
    <div class="wrap projects__foot">
      <div class="rail__progress" aria-hidden="true"><span></span></div>
      <div class="rail__arrows">
        <button class="icon-btn" type="button" data-rail-prev aria-label="Anterior">{ico('i-chev-l')}</button>
        <button class="icon-btn" type="button" data-rail-next aria-label="Siguiente">{ico('i-chev-r')}</button>
      </div>
    </div>"""


def iniciales(nombre):
    return "".join(p[0] for p in nombre.split()[:2]).upper()


def sec_testimonios():
    o = GEN["testimonios"]
    if not o["lista"]:
        return ""
    items = "\n".join(f"""        <li class="quote">
          <svg class="quote__mark" aria-hidden="true"><use href="#i-quote"/></svg>
          <p class="quote__lead">{e(t['cita'])}</p>
          <p class="quote__text">{e(t['texto'])}</p>
          <p class="quote__who"><span class="quote__avatar" aria-hidden="true">{e(iniciales(t['nombre']))}</span><span><strong>{e(t['nombre'])}</strong> {e(t['detalle'])}</span></p>
        </li>""" for t in o["lista"])
    return f"""  <section class="sec quotes" id="testimonios" aria-labelledby="quotes-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">{e(o['eyebrow'])}</p>
        <h2 class="title" id="quotes-title">{tit(o)}</h2>
      </div>
    </div>
    <div class="rail rail--quotes" data-rail>
      <ul class="rail__track" role="list" tabindex="0" aria-label="Testimonios. Desliza para ver más.">
{items}
      </ul>
    </div>
    <div class="wrap projects__foot">
      <div class="rail__progress" aria-hidden="true"><span></span></div>
      <div class="rail__arrows">
        <button class="icon-btn" type="button" data-rail-prev aria-label="Testimonio anterior">{ico('i-chev-l')}</button>
        <button class="icon-btn" type="button" data-rail-next aria-label="Testimonio siguiente">{ico('i-chev-r')}</button>
      </div>
    </div>
  </section>
"""


def sec_faq(n, enlace=False):
    o = GEN["faq"]
    items = "\n".join(f"""        <details class="faq__item">
          <summary>{e(f['pregunta'])}<svg class="chev" aria-hidden="true"><use href="#i-chev-d"/></svg></summary>
          <p>{en_linea(f['respuesta'])}</p>
        </details>""" for f in o["lista"])
    mas = f'\n        <p class="faq__more">¿Tienes otra pregunta? <a href="{R(n)["u"]("contacto.html")}">Escríbenos</a></p>' if enlace else ""
    return f"""  <section class="sec faq" id="preguntas" aria-labelledby="faq-title">
    <div class="wrap faq__grid">
      <div class="sec__head reveal">
        <p class="eyebrow">{e(o['eyebrow'])}</p>
        <h2 class="title" id="faq-title">{tit(o)}</h2>{mas}
      </div>
      <div class="faq__list reveal">
{items}
      </div>
    </div>
  </section>
"""


def banda(n, cta=None, href="contacto.html"):
    o = GEN["banda"]
    s = stem(o["foto"])
    w, h = medida(o["foto"])
    return f"""  <section class="band on-dark" aria-labelledby="band-title">
    <picture class="band__media" aria-hidden="true">
      <img src="{R(n)['F']}{s}-800.webp" width="{w}" height="{h}" loading="lazy" decoding="async" alt="">
    </picture>
    <div class="wrap band__in reveal">
      <h2 class="band__title display" id="band-title">{tit(o)}</h2>
      <p class="lead">{e(o['texto'])}</p>
      <a class="btn btn--light btn--lg" href="{R(n)['u'](href)}">{e(cta or o['boton'])} {ico('i-arrow')}</a>
    </div>
  </section>
"""


def tarjeta(a, n, cabeza="h3"):
    r = R(n)
    href = r["u"]("blog/" + a["url"] + ".html")
    w, h = medida(a["foto"])
    return f"""<li class="post" data-cat="{e(a['categoria'])}">
  <a class="post__link" href="{href}">
    <div class="post__media"><img src="{r['F']}{stem(a['foto'])}-800.webp" width="{w}" height="{h}" loading="lazy" decoding="async" alt=""></div>
    <div class="post__body">
      <p class="post__meta"><span class="post__cat">{e(a['categoria'])}</span><span>{a['lectura']} min de lectura</span></p>
      <{cabeza} class="post__title">{tit(a)}</{cabeza}>
      <p class="post__excerpt">{e(a['resumen'])}</p>
      <span class="post__more">Leer artículo {ico('i-arrow')}</span>
    </div>
  </a>
</li>"""


def sec_blog(n, o, lista):
    if not lista:
        return ""
    t = "\n".join(tarjeta(a, n) for a in lista)
    return f"""  <section class="sec blog-teaser" aria-labelledby="bt-title">
    <div class="wrap">
      <div class="sec__head bt__head reveal">
        <div>
          <p class="eyebrow">{e(o['eyebrow'])}</p>
          <h2 class="title" id="bt-title">{tit(o)}</h2>
        </div>
        <a class="link-arrow" href="{R(n)['u']('blog/index.html')}">{e(o['enlace'])} {ico('i-arrow')}</a>
      </div>
    </div>
    <div class="rail rail--posts" data-rail>
      <ul class="rail__track" role="list" tabindex="0" aria-label="Artículos del blog. Desliza para ver más.">
{t}
      </ul>
    </div>
  </section>
"""


def historia(n, o, id_, boton=""):
    """Foto con sello + texto (Sobre OMBU en Inicio, Quiénes somos en Nosotros)."""
    A, u = R(n)["A"], R(n)["u"]
    parrafos = "\n".join(f"        <p>{en_linea(p)}</p>" for p in o["parrafos"])
    cta = f'\n        <a class="btn btn--lg story__cta" href="{u("nosotros.html")}">{e(boton)} {ico("i-arrow")}</a>' if boton else ""
    return f"""  <section class="sec story" aria-labelledby="{id_}">
    <div class="wrap story__grid">
      <figure class="story__media reveal">
        {foto(o['foto'], n, o['alt'])}
        <div class="story__badge" aria-hidden="true">
          <svg viewBox="0 0 2250 2250"><use href="{A}img/marca.svg#ombu-mark"/></svg>
        </div>
      </figure>
      <div class="story__copy reveal">
        <p class="eyebrow">{e(o['eyebrow'])}</p>
        <h2 class="title" id="{id_}">{tit(o)}</h2>
{parrafos}{cta}
      </div>
    </div>
  </section>
"""


# ---------------------------------------------------------------- páginas

def pag_inicio():
    P = PAG["inicio"]
    h, pr = P["portada"], P["proyectos"]
    F, s = R(0)["F"], stem(h["foto"])
    w, alto = medida(h["foto"])
    preload = f"""  <link rel="preload" as="image" href="{F}{s}-800.webp" imagesrcset="{F}{s}-800.webp 800w, {F}{s}.webp {w}w" imagesizes="100vw">
  <script type="application/ld+json">
  {json.dumps({"@context": "https://schema.org", "@type": "GeneralContractor", "name": "OMBU Renovaciones", "url": URL, "logo": URL + "assets/img/icon-512.png",
               "image": URL + "assets/img/og-sitio.jpg", "description": P["seo"]["descripcion"], "telephone": C["whatsapp"], "areaServed": C["ubicacion"],
               "address": {"@type": "PostalAddress", "addressLocality": "Medellín", "addressRegion": "Antioquia", "addressCountry": "CO"},
               "sameAs": [C["instagram_url"], C["facebook_url"]]}, ensure_ascii=False)}
  </script>
"""
    garantias = "\n".join(f"        <li>{ico('i-check')} {e(g)}</li>" for g in h["garantias"])
    destacados = [p["url"] for p in PROYECTOS if p.get("destacado")]
    cuerpo = f"""
  <!-- ============ Hero ============ -->
  <section class="hero on-dark" id="inicio" aria-labelledby="hero-title">
    <picture class="hero__media">
      <img src="{F}{s}-800.webp" srcset="{F}{s}-800.webp 800w, {F}{s}.webp {w}w" sizes="100vw" width="{w}" height="{alto}" fetchpriority="high" alt="{e(h['alt'])}">
    </picture>
    <div class="hero__body wrap">
      <p class="eyebrow">{e(h['eyebrow'])}</p>
      <h1 class="hero__title display" id="hero-title">{tit(h)}</h1>
      <p class="hero__lead">{e(h['texto'])}</p>
      <div class="hero__ctas">
        <a class="btn btn--light btn--lg" href="contacto.html">{e(h['boton'])} {ico('i-arrow')}</a>
        <a class="btn btn--ghost btn--lg" href="proyectos.html">{e(h['boton2'])}</a>
      </div>
      <ul class="hero__trust" aria-label="Garantías">
{garantias}
      </ul>
    </div>
  </section>

{historia(0, P['sobre'], 'story-title', P['sobre']['boton'])}
{sec_servicios(0, P['servicios'], P['servicios']['boton'])}
{sec_pasos(0)}
  <!-- ============ Proyectos destacados ============ -->
  <section class="sec projects" id="proyectos" aria-labelledby="projects-title">
    <div class="wrap">
      <div class="sec__head projects__head reveal">
        <div>
          <p class="eyebrow">{e(pr['eyebrow'])}</p>
          <h2 class="title" id="projects-title">{tit(pr)}</h2>
        </div>
        <div class="badge" aria-hidden="true"><strong>{e(pr['cifra'])}</strong><span>{e(pr['cifra_txt'])}</span></div>
      </div>
      <p class="lead projects__lead reveal">{e(pr['texto'])} <span class="sr-only">{e(pr['cifra'])} {e(pr['cifra_txt'])}.</span></p>
    </div>
{carril(destacados, "Proyectos destacados")}
    <div class="wrap"><a class="btn btn--lg sec__cta" href="proyectos.html">{e(pr['boton'])} {ico('i-arrow')}</a></div>
  </section>

{sec_por_que(0, P['por_que'])}
{sec_testimonios()}
{sec_faq(0, enlace=True)}
{sec_blog(0, P['blog'], ARTICULOS[:3])}
{banda(0)}"""
    return pagina(P["seo"], 0, "inicio", "inicio", cuerpo, js=("inicio.js",), extra_head=preload, extra_body=dialogos())


def pag_nosotros():
    P = PAG["nosotros"]
    etapas, k = [], 0
    for i, et in enumerate(P["proceso"]["etapas"], 1):
        items = "".join(f'<li value="{k + j}">{e(p)}</li>' for j, p in enumerate(et["pasos"], 1))
        k += len(et["pasos"])
        etapas.append(f"""        <li class="stage reveal">
          <p class="stage__n">Etapa {i}</p>
          <h3 class="stage__title">{e(et['titulo'])}</h3>
          <ol class="stage__list">{items}</ol>
        </li>""")
    equipo = "\n".join(
        f"        <li>{foto(x['foto'], 0, x['texto'], '(min-width: 600px) 33vw, 100vw') if x['foto'] else pendiente('Foto pendiente: ' + x['texto'])}<p>{e(x['texto'])}</p></li>"
        for x in P["equipo"]["fotos"])
    nl = "\n"
    pr, eq = P["proceso"], P["equipo"]
    cuerpo = phero(P["portada"], [("Inicio", "index.html"), ("Nosotros", None)]) + f"""
{historia(0, P['quienes'], 'who-title')}
{sec_por_que(0, P['diferencia'])}
  <!-- ============ Cómo trabajamos ============ -->
  <section class="sec stages" id="proceso" aria-labelledby="stages-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">{e(pr['eyebrow'])}</p>
        <h2 class="title" id="stages-title">{tit(pr)}</h2>
        <p class="lead">{e(pr['texto'])}</p>
      </div>
      <ol class="stages__grid" role="list">
{nl.join(etapas)}
      </ol>
    </div>
  </section>

  <!-- ============ Equipo ============ -->
  <section class="sec team" aria-labelledby="team-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">{e(eq['eyebrow'])}</p>
        <h2 class="title" id="team-title">{tit(eq)}</h2>
        <p class="lead">{e(eq['texto'])}</p>
      </div>
      <ul class="team__grid reveal" role="list">
{equipo}
      </ul>
    </div>
  </section>

{banda(0, P['cta']['boton'])}"""
    return pagina(P["seo"], 0, "nosotros", "nosotros", cuerpo)


def pag_servicios():
    P = PAG["servicios"]
    cuerpo = (phero(P["portada"], [("Inicio", "../index.html"), ("Servicios", None)])
              + sec_servicios(1, P["lista"]) + sec_pasos(1) + sec_faq(1, enlace=True) + banda(1))
    return pagina(P["seo"], 1, "servicios", "servicios", cuerpo)


def pag_servicio(s):
    lista = "\n".join(f"        <li>{ico('i-check')}<span>{e(x)}</span></li>" for x in s["lista"])
    catalogo = ""
    if s.get("piezas"):
        piezas = "\n".join(
            f"        <li>{foto(p['foto'], 1, p['nombre'], '(min-width: 600px) 33vw, 100vw') if p['foto'] else pendiente('Foto pendiente', 'ph--sq')}<p>{e(p['nombre'])}</p></li>"
            for p in s["piezas"])
        catalogo = f"""
  <section class="sec catalog" aria-labelledby="cat-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">Catálogo</p>
        <h2 class="title" id="cat-title">{e(s['catalogo_titulo'])} <em>{e(s['catalogo_titulo_em'])}</em></h2>
        <p class="lead">{e(s['catalogo_texto'])}</p>
      </div>
      <ul class="team__grid team__grid--3" role="list">
{piezas}
      </ul>
    </div>
  </section>
"""
    cta = f"contacto.html?servicio={quote(s['nombre'])}"
    media = foto(s["foto"], 1, s["alt"], lazy=False) if s["foto"] else pendiente("Foto pendiente")
    cuerpo = f"""  <section class="shero" aria-labelledby="page-title">
    <div class="wrap shero__grid">
      <div class="shero__copy">
        <nav class="crumbs" aria-label="Ruta"><a href="../index.html">Inicio</a><span aria-hidden="true">/</span><a href="index.html">Servicios</a><span aria-hidden="true">/</span><span aria-current="page">{e(s['nombre'])}</span></nav>
        <p class="eyebrow">{SERVICIOS.index(s) + 1:02d} · {e(s['nombre'])}</p>
        <h1 class="display shero__title" id="page-title">{tit(s)}</h1>
        <p class="lead">{e(s['texto'])}</p>
        <a class="btn btn--lg shero__cta" href="../{cta}">{e(s['cta'])} {ico('i-arrow')}</a>
      </div>
      <figure class="shero__media">{media}</figure>
    </div>
  </section>

  <section class="sec incl" aria-labelledby="incl-title">
    <div class="wrap incl__grid">
      <div class="sec__head reveal">
        <span class="svc__ico svc__ico--lg">{ico(s['icono'])}</span>
        <h2 class="title" id="incl-title">{e(s['lista_titulo'])}</h2>
      </div>
      <ul class="incl__list reveal" role="list">
{lista}
      </ul>
    </div>
  </section>
{catalogo}
{sec_servicios(1, PAG['servicios']['otros'], ocultar=[s['url'], *s.get('ocultar', [])])}
{banda(1, s['cta'], cta)}"""
    return pagina({"titulo": f"{s['nombre']} · Servicios OMBU Renovaciones", "descripcion": s["texto"]}, 1, "svc-" + s["url"], "servicio", cuerpo)


def pag_proyectos():
    P = PAG["proyectos"]
    o = P["portada"]
    badge = f'\n      <div class="badge bhero__badge" aria-hidden="true"><strong>{e(o["cifra"])}</strong><span>{e(o["cifra_txt"])}</span></div>'
    cuerpo = (phero(o, [("Inicio", "index.html"), ("Proyectos", None)], badge)
              + f"""  <section class="sec projects pgal" id="todos" aria-label="Proyectos">
    <div class="wrap">
      <ul class="pgrid" data-proj="{",".join(p["url"] for p in PROYECTOS)}" role="list"></ul>
    </div>
  </section>
""" + banda(0, P["cta"]["boton"]))
    return pagina(P["seo"], 0, "proyectos", "proyectos", cuerpo, js=("inicio.js",), extra_body=dialogos())


def pag_contacto():
    P = PAG["contacto"]
    o, f_ = P["portada"], P["formulario"]
    chips = "\n".join(f'            <label class="chip"><input type="radio" name="espacio" value="{e(v)}"{" checked" if i == 0 else ""}><span>{e(v)}</span></label>'
                      for i, v in enumerate(f_["opciones"]))

    def campo(id_, nombre, label, tipo, auto, extra=""):
        return f"""          <div class="field">
            <label for="f-{id_}">{label}</label>
            <input id="f-{id_}" name="{nombre}" type="{tipo}" autocomplete="{auto}" required aria-describedby="e-{id_}"{extra}>
            <p class="field__err" id="e-{id_}" aria-live="polite"></p>
          </div>"""
    cuerpo = f"""  <section class="sec contact contact--page" id="contacto" aria-labelledby="page-title">
    <div class="wrap contact__grid">
      <div class="contact__copy">
        <nav class="crumbs" aria-label="Ruta"><a href="index.html">Inicio</a><span aria-hidden="true">/</span><span aria-current="page">Contacto</span></nav>
        <h1 class="display bhero__title" id="page-title">{tit(o)}</h1>
        <p class="lead">{e(o['texto'])}</p>
        <ul class="channels" role="list">
          <li><a class="channel" href="{WA}" target="_blank" rel="noopener"><span class="channel__ico">{ico('i-wa')}</span><span><small>WhatsApp</small>{e(C['whatsapp'])}</span></a></li>
          <li><a class="channel" href="{e(C['instagram_url'])}" target="_blank" rel="noopener"><span class="channel__ico">{ico('i-ig')}</span><span><small>Instagram</small>{e(C['instagram_txt'])}</span></a></li>
          <li><div class="channel"><span class="channel__ico">{ico('i-pin')}</span><span><small>Ubicación</small>{e(C['ubicacion'])}</span></div></li>
        </ul>
      </div>

      <div class="form-wrap">
        <form class="form" id="form" novalidate>
          <h2 class="form__title">{e(f_['titulo'])}</h2>
          <p class="form__hint">{e(f_['ayuda'])}</p>
          <div class="form__row">
{campo("name", "nombre", "Nombre", "text", "given-name")}
{campo("last", "apellido", "Apellido", "text", "family-name")}
          </div>
          <div class="form__row">
{campo("phone", "celular", "Celular", "tel", "tel", ' inputmode="tel" placeholder="300 123 4567"')}
{campo("city", "ciudad", "Ciudad", "text", "address-level2", ' placeholder="Medellín"')}
          </div>
          <fieldset class="field">
            <legend>{e(f_['pregunta_espacio'])}</legend>
            <div class="chips">
{chips}
            </div>
          </fieldset>
          <div class="field">
            <label for="f-msg">{e(f_['idea'])} <span class="field__opt">(opcional)</span></label>
            <textarea id="f-msg" name="mensaje" rows="4" placeholder="{e(f_['idea_ejemplo'])}"></textarea>
          </div>
          <div class="field">
            <label class="check"><input id="f-ok" type="checkbox" name="autorizo" required aria-describedby="e-ok"><span>Acepto los <a href="legal/terminos-y-condiciones.html" target="_blank">términos y condiciones</a> y autorizo a OMBU Renovaciones a tratar mis datos personales según su <a href="legal/politica-de-datos.html" target="_blank">política de tratamiento de datos</a>.</span></label>
            <p class="field__err" id="e-ok" aria-live="polite"></p>
          </div>
          <button class="btn btn--lg btn--block form__submit" type="submit">{e(f_['boton'])} {ico('i-arrow')}</button>
          <p class="form__note">{e(f_['nota'])}</p>
        </form>
        <div class="form form--ok" id="form-ok" tabindex="-1" hidden>
          <span class="form__ok-ico">{ico('i-check')}</span>
          <h2 class="form__title">{e(f_['gracias_titulo'])}</h2>
          <p>{e(f_['gracias_texto'])}</p>
          <p class="form__note">¿No se abrió WhatsApp? <a id="form-wa" href="{WA}" target="_blank" rel="noopener">Envía tu mensaje aquí</a>.</p>
        </div>
      </div>
    </div>
  </section>

{sec_faq(0)}"""
    return pagina(P["seo"], 0, "contacto", "contacto", cuerpo, js=("inicio.js",), antes_js='<script src="admin/config.js"></script>\n')


def pag_blog_indice():
    P = PAG["blog"]
    migas = [("Inicio", "../index.html"), ("Blog", None)]
    if not ARTICULOS:
        return pagina(P["seo"], 1, "blog", "blog", phero(P["portada"], migas) + banda(1), js=("blog.js",))
    d = ARTICULOS[0]
    resto = "\n".join(tarjeta(a, 1) for a in ARTICULOS[1:])
    cats = sorted({a["categoria"] for a in ARTICULOS})
    chips = "\n".join(f'          <button class="filter" type="button" aria-pressed="false" data-filter="{e(c)}">{e(c)}</button>' for c in cats)
    cuerpo = phero(P["portada"], migas) + f"""
  <section class="wrap blist" aria-label="Artículos">
    <article class="feature reveal" data-cat="{e(d['categoria'])}">
      <a class="feature__link" href="{d['url']}.html">
        <div class="feature__media">{foto(d['foto'], 1, d['alt'], '(min-width: 960px) 700px, 100vw', lazy=False)}</div>
        <div class="feature__body">
          <p class="post__meta"><span class="post__cat">{e(d['categoria'])}</span><span>{fecha_larga(d['fecha'])}</span><span>{d['lectura']} min</span></p>
          <h2 class="feature__title">{tit(d)}</h2>
          <p class="post__excerpt">{e(d['resumen'])}</p>
          <span class="btn">Leer artículo {ico('i-arrow')}</span>
        </div>
      </a>
    </article>

    <div class="filters" role="group" aria-label="Filtrar por tema">
      <button class="filter" type="button" aria-pressed="true" data-filter="">Todos</button>
{chips}
    </div>
    <ul class="posts" id="posts" role="list">
{tarjeta(d, 1, 'h2').replace('<li class="post"', '<li class="post post--dup"')}
{resto.replace('<h3 class="post__title">', '<h2 class="post__title">').replace('</h3>', '</h2>')}
    </ul>
    <p class="posts__empty" id="posts-empty" hidden>Todavía no hay artículos en este tema.</p>
  </section>

""" + banda(1)
    return pagina(P["seo"], 1, "blog", "blog", cuerpo, js=("blog.js",))


def pag_articulo(a):
    otros = [x for x in ARTICULOS if x["url"] != a["url"]]
    titulo_txt = f'{a["titulo"]} {a["titulo_em"]}'
    ld = f"""  <script type="application/ld+json">
  {json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": titulo_txt, "description": a["resumen"], "datePublished": a["fecha"],
               "image": f"{URL}fotos/{stem(a['foto'])}.webp", "author": {"@type": "Organization", "name": "OMBU Renovaciones"}}, ensure_ascii=False)}
  </script>
"""
    share = quote(f"{titulo_txt} · OMBU Renovaciones")
    pie_foto = f"<figcaption>{e(a['pie_foto'])}</figcaption>" if a.get("pie_foto") else ""
    cuerpo = f"""  <article class="art">
    <header class="art__head wrap">
      <nav class="crumbs" aria-label="Ruta"><a href="../index.html">Inicio</a><span aria-hidden="true">/</span><a href="index.html">Blog</a><span aria-hidden="true">/</span><span aria-current="page">{e(a['categoria'])}</span></nav>
      <p class="post__meta"><span class="post__cat">{e(a['categoria'])}</span><span><time datetime="{a['fecha']}">{fecha_larga(a['fecha'])}</time></span><span>{a['lectura']} min de lectura</span></p>
      <h1 class="display art__title">{tit(a)}</h1>
      <p class="lead art__lead">{e(a['resumen'])}</p>
      <p class="art__by"><span class="art__avatar" aria-hidden="true"><svg viewBox="0 0 2250 2250"><use href="../assets/img/marca.svg#ombu-mark"/></svg></span><span><strong>{e(a['autor'])}</strong>Diseño y construcción</span></p>
    </header>
    <figure class="art__cover wrap">
      {foto(a['foto'], 1, a['alt'], '(min-width: 960px) 1100px, 100vw', lazy=False)}
      {pie_foto}
    </figure>
    <div class="art__layout wrap">
      <div class="prose">
{md(a['cuerpo'], 1, lead=True)}
      </div>
      <aside class="art__side">
        <div class="share" aria-label="Compartir">
          <p>Compartir</p>
          <a class="icon-btn" href="https://wa.me/?text={share}%20" data-share-wa target="_blank" rel="noopener" aria-label="Compartir por WhatsApp">{ico('i-wa')}</a>
          <button class="icon-btn" type="button" data-copy aria-label="Copiar enlace">{ico('i-link')}</button>
          <span class="share__ok" role="status"></span>
        </div>
      </aside>
    </div>
    <section class="wrap art__cta reveal" aria-labelledby="cta-title">
      <div class="cta-box on-dark">
        <svg class="cta-box__mark" viewBox="0 0 2250 2250" aria-hidden="true"><use href="../assets/img/marca.svg#ombu-mark"/></svg>
        <h2 class="cta-box__title" id="cta-title">¿Quieres transformar <em>tu espacio?</em></h2>
        <p>Cuéntanos qué tienes en mente. La primera reunión es gratuita.</p>
        <div class="cta-box__btns">
          <a class="btn btn--light btn--lg" href="../contacto.html">Empezar mi proyecto {ico('i-arrow')}</a>
          <a class="btn btn--ghost btn--lg" href="{e(WA_COTIZAR)}" target="_blank" rel="noopener">{ico('i-wa')} WhatsApp</a>
        </div>
      </div>
    </section>
  </article>

{sec_blog(1, {"eyebrow": "Sigue leyendo", "titulo": "Más ideas", "titulo_em": "del blog", "enlace": "Ver todo el blog"}, otros)}"""
    return pagina({"titulo": f"{titulo_txt} · Blog OMBU", "descripcion": a["resumen"]}, 1, "blog", "articulo", cuerpo, js=("blog.js",), og="article", extra_head=ld)


def pag_legal(archivo):
    o = PAG[archivo]["documento"]
    nombre = dict(LEGALES)[archivo]
    otros = "".join(f'<li><a href="{f}.html"{" aria-current=\"page\"" if f == archivo else ""}>{t}</a></li>' for f, t in LEGALES)
    cuerpo = f"""  <article class="art legal">
    <header class="art__head wrap">
      <nav class="crumbs" aria-label="Ruta"><a href="../index.html">Inicio</a><span aria-hidden="true">/</span><span aria-current="page">{nombre}</span></nav>
      <h1 class="display art__title">{tit(o)}</h1>
      <p class="lead art__lead">{e(o['texto'])}</p>
      <p class="post__meta"><span>Vigente desde el {e(o['vigencia'])}</span></p>
    </header>
    <div class="wrap legal__body">
      <div class="prose">
{md(o['cuerpo'], 1)}
      </div>
      <nav class="legal__nav" aria-label="Documentos legales">
        <p>Documentos legales</p>
        <ul role="list">{otros}</ul>
      </nav>
    </div>
  </article>
"""
    return pagina({"titulo": f"{o['titulo']} {o['titulo_em']} · OMBU Renovaciones", "descripcion": o["texto"]}, 1, "", "legal", cuerpo)


# ---------------------------------------------------------------- escritura

def datos_proyectos():
    """assets/js/proyectos.js del sitio: fotos con medidas, para las tarjetas, la ficha y el visor."""
    def ph(f):
        return [stem(f), *medida(f)]
    lista = [{"slug": p["url"], "nombre": p["nombre"], "tipo": p.get("tipo", ""), "servicios": p.get("servicios", ""), "descripcion": p.get("descripcion", ""),
              "par": [ph(p["foto_antes"]), ph(p["foto_despues"])] if p.get("foto_antes") and p.get("foto_despues") else None,
              "despues": [ph(f) for f in p["despues"]], "antes": [ph(f) for f in p["antes"]]} for p in PROYECTOS]
    return "window.OMBU_PROYECTOS = " + json.dumps(lista, ensure_ascii=False, separators=(",", ":")) + ";\n"


def main():
    for x in os.listdir(DIST):
        if x != "fotos":
            ruta = os.path.join(DIST, x)
            shutil.rmtree(ruta) if os.path.isdir(ruta) else os.remove(ruta)
    shutil.copytree(os.path.join(RAIZ, "assets"), os.path.join(DIST, "assets"), ignore=shutil.ignore_patterns("proyectos", "hero-*", "fondo-*", "comparador-*"))
    shutil.copytree(os.path.join(RAIZ, "panel"), os.path.join(DIST, "admin"))
    with open(os.path.join(DIST, "assets/js/proyectos.js"), "w", encoding="utf-8") as f:
        f.write(datos_proyectos())

    paginas = {
        "index.html": pag_inicio(),
        "nosotros.html": pag_nosotros(),
        "proyectos.html": pag_proyectos(),
        "contacto.html": pag_contacto(),
        "servicios/index.html": pag_servicios(),
        "blog/index.html": pag_blog_indice(),
        # la dirección anterior del sitio
        "sitio/index.html": '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=../"><link rel="canonical" href="../"><a href="../">OMBU Renovaciones</a>\n',
    }
    for s in SERVICIOS:
        paginas["servicios/" + s["url"] + ".html"] = pag_servicio(s)
    for a in ARTICULOS:
        paginas["blog/" + a["url"] + ".html"] = pag_articulo(a)
    for f, _ in LEGALES:
        paginas["legal/" + f + ".html"] = pag_legal(f)
    for ruta, contenido in paginas.items():
        ruta = os.path.join(DIST, ruta)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)

    # Lo que necesita el dominio: robots, sitemap y las direcciones del sitio anterior
    rutas = [r for r in paginas if not r.startswith("sitio/")]
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {URL}sitemap.xml\n")
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "".join(f"  <url><loc>{URL}{'' if r == 'index.html' else r.replace('index.html', '')}</loc></url>\n" for r in rutas) + "</urlset>\n")
    with open(os.path.join(DIST, ".htaccess"), "w", encoding="utf-8") as f:
        f.write("""DirectoryIndex index.html
Options -Indexes
<IfModule mod_headers.c>
Header always set Strict-Transport-Security "max-age=31536000"
</IfModule>
RewriteEngine On
RewriteCond %{HTTPS} !=on
RewriteCond %{HTTP:X-Forwarded-Proto} !=https
RewriteRule ^ https://omburenovaciones.com%{REQUEST_URI} [L,R=301]
RewriteCond %{HTTP_HOST} ^www\\. [NC]
RewriteRule ^ https://omburenovaciones.com%{REQUEST_URI} [L,R=301]
# Direcciones del sitio anterior (WordPress)
RewriteRule ^proyectos/?$ /proyectos.html [L,R=301]
RewriteRule ^proyectoss/?$ /proyectos.html [L,R=301]
RewriteRule ^contacto/?$ /contacto.html [L,R=301]
RewriteRule ^por-que-elegirnos/?$ /nosotros.html [L,R=301]
RewriteRule ^inicio/?$ / [L,R=301]
""")

    # Datos para ver el panel en modo demo (/admin/?demo) sin Supabase
    with open(os.path.join(DIST, "admin/demo.json"), "w", encoding="utf-8") as f:
        json.dump({"paginas": PAG, "servicios": carpeta("servicios"), "proyectos": carpeta("proyectos"), "blog": carpeta("blog")}, f, ensure_ascii=False)
    print("Generadas", len(paginas), "páginas en dist/")


if __name__ == "__main__":
    main()
