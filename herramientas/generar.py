# -*- coding: utf-8 -*-
"""Genera todas las páginas del sitio de OMBU.

    python3 herramientas/generar.py

Escribe en sitio/: index.html, nosotros.html, proyectos.html, contacto.html,
servicios/ (índice + una página por servicio), blog/ (índice + artículos de
herramientas/articulos.py) y legal/politica-de-datos.html.

Así la cabecera, el menú, el pie y las secciones repetidas son idénticas en todas las páginas.
Textos según «OMBU | Estructura y contenidos página web». Lo que falta (fotos, datos legales)
sale marcado «pendiente»: no se inventa.
"""
import html
import json
import os
from urllib.parse import quote

from articulos import ARTICULOS

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITIO = os.path.join(RAIZ, "sitio")
WA = "https://wa.me/573105996809"
WA_COTIZAR = WA + "?text=Hola%20OMBU%2C%20quiero%20cotizar%20la%20renovaci%C3%B3n%20de%20mi%20espacio."
URL = "https://feliperpovera.github.io/ombu-renovaciones/"
LEGAL = "legal/politica-de-datos.html"

ARTICULOS = sorted(ARTICULOS, key=lambda a: a["fecha"], reverse=True)

# (clave, texto, ruta desde sitio/)
MENU = [
    ("inicio", "Inicio", "index.html"),
    ("nosotros", "Nosotros", "nosotros.html"),
    ("servicios", "Servicios", "servicios/index.html"),
    ("proyectos", "Proyectos", "proyectos.html"),
    ("blog", "Blog", "blog/index.html"),
    ("contacto", "Contacto", "contacto.html"),
]

SERVICIOS = [
    {"slug": "diseno", "n": "01", "nombre": "Diseño", "ico": "i-design",
     "resumen": "Convertimos tus ideas en espacios funcionales y personalizados, definiendo cada detalle antes de comenzar.",
     "titulo": "Diseñamos espacios", "titulo_em": "que se sienten tuyos.",
     "texto": "Transformamos tus ideas en propuestas que combinan estética, funcionalidad y personalidad. Cada decisión de diseño parte de tus necesidades y de la manera en que quieres vivir o utilizar el espacio.",
     "lista_titulo": "¿Qué incluye?",
     "lista": ["Desarrollo de propuestas de diseño.", "Renders.", "Planos.", "Detalles de carpintería.", "Selección de materiales y acabados."],
     "cta": "Quiero diseñar mi espacio", "foto": ("kuna-1002", "d02", 1024, 683)},
    {"slug": "construccion", "n": "02", "nombre": "Construcción", "ico": "i-build",
     "resumen": "Materializamos los diseños con nuestro equipo técnico, procesos definidos y acompañamiento durante toda la obra.",
     "titulo": "De los planos", "titulo_em": "a la realidad.",
     "texto": "Ejecutamos proyectos de construcción y renovación con una planificación clara, coordinación técnica y un equipo que acompaña cada etapa.",
     "lista_titulo": "¿Qué incluye?",
     "lista": ["Diagnóstico técnico.", "Coordinación de materiales y personal.", "Planimetría.", "Ejecución de las actividades de obra.", "Seguimiento del cronograma."],
     "cta": "Quiero transformar mi espacio", "foto": ("torrealta", "d01", 1024, 683)},
    {"slug": "mobiliario", "n": "03", "nombre": "Mobiliario", "ico": "i-sofa",
     "resumen": "Creamos y seleccionamos piezas que complementan tus espacios con identidad, funcionalidad y diseño.",
     "titulo": "Los detalles que", "titulo_em": "completan tu espacio.",
     "texto": "Complementamos nuestros proyectos con piezas de mobiliario exclusivas y soluciones hechas a la medida que responden a las características de cada ambiente.",
     "lista_titulo": "Lo que ofrecemos",
     "lista": ["Catálogo de 10 a 15 productos exclusivos.", "Opciones personalizadas para tu espacio."],
     "cta": "Conocer mobiliario", "foto": ("aires-del-campestre", "d01", 1024, 683)},
    {"slug": "interventoria", "n": "04", "nombre": "Interventoría", "ico": "i-clipboard",
     "resumen": "Supervisamos proyectos para verificar el cumplimiento técnico, la calidad y los cronogramas establecidos.",
     "titulo": "Supervisión que", "titulo_em": "da tranquilidad.",
     "texto": "Acompañamos y supervisamos proyectos de construcción para verificar el cumplimiento de criterios técnicos, cronogramas, actividades y estándares de calidad.",
     "lista_titulo": "Espacios que atendemos",
     "lista": ["Viviendas.", "Locales comerciales.", "Oficinas de gran formato.", "Conjuntos residenciales y administraciones."],
     "cta": "Solicitar acompañamiento", "foto": ("palo-alto", "d01", 1024, 683)},
]

ATRIBUTOS = [
    ("i-shield", "Confianza y respaldo", "Certificaciones, pólizas y procesos que aportan seguridad a cada proyecto."),
    ("i-design", "Diseño a la medida", "Soluciones pensadas alrededor de tus necesidades."),
    ("i-compare", "Experiencia comprobada", "Proyectos y transformaciones que muestran nuestro trabajo."),
    ("i-chat", "Acompañamiento cercano", "Profesionales presentes en cada etapa."),
    ("i-people", "Equipo propio", "Integramos diseño, interiorismo, construcción, mano de obra y logística."),
]

PASOS = [
    ("i-chat", "Nos cuentas tu idea", "Nos reunimos para conocer tus necesidades, expectativas y el espacio que quieres transformar."),
    ("i-plan", "Diseñamos a tu medida", "Desarrollamos una propuesta personalizada, ajustamos los detalles y definimos el presupuesto."),
    ("i-build", "Construimos con respaldo", "Nuestro equipo ejecuta el proyecto con acompañamiento, seguimiento y reportes periódicos."),
    ("i-key", "Entregamos lo acordado", "Revisamos los detalles finales y hacemos entrega del proyecto terminado."),
]

ETAPAS = [
    ("Nos conocemos", ["Nos compartes tu idea o necesidad.", "Nuestro equipo comercial te recibe.",
                       "Agendamos una reunión para conocerte.", "Preparamos un plan de trabajo personalizado."]),
    ("Diseñamos contigo", ["Realizamos el levantamiento del espacio y conocemos tus expectativas.", "Desarrollamos una propuesta inicial.",
                           "Revisamos y ajustamos el diseño contigo.", "Aprobamos los diseños y el presupuesto."]),
    ("Hacemos realidad el proyecto", ["Iniciamos la etapa de obra.",
                                      "Ejecutamos el proyecto con director general, residente, personal de obra y acompañamiento comercial. Compartimos informes semanales y programamos visitas de seguimiento cuando lo solicitas."]),
    ("Entregamos", ["Realizamos la entrega final del proyecto."]),
]

FAQ = [
    ("¿La primera reunión tiene algún costo?", "No. Nuestra primera reunión es gratuita y nos permite conocer tu idea, entender lo que necesitas y conversar sobre las posibilidades de tu proyecto."),
    ("¿Cuánto tiempo tarda un proyecto?", "Depende del alcance y las necesidades de cada espacio. Como referencia, la etapa de diseño puede tomar entre 30 y 45 días, mientras que una obra puede tardar entre 90 y 180 días."),
    ("¿El precio de mi proyecto puede cambiar?", "Trabajamos con presupuestos cerrados. El valor cotizado se mantiene de acuerdo con el alcance aprobado inicialmente."),
    ("¿De qué depende el costo de un proyecto?", "El presupuesto depende de las características de cada intervención, incluyendo materiales seleccionados, áreas que se van a transformar, iluminación y posibles redistribuciones del espacio."),
]

# Textuales de omburenovaciones.com
TESTIMONIOS = [
    ("EO", "Emilio Ortega", "Renovación total de apartamento",
     "«Hice la renovación total de mi apartamento con Ombu y, sinceramente, fue una de las mejores decisiones que he tomado.»",
     "Desde el primer día se encargaron absolutamente de todo. Yo solo conté cómo quería mi espacio y ellos se encargaron de convertir esa idea en algo incluso mejor de lo que imaginé. Los acabados, los materiales y los detalles son de primera. Se nota el cuidado y la calidad en cada rincón. Recomiendo a Ombu sin dudarlo. Son profesionales, cumplidos y el resultado final habla por ellos."),
    ("LD", "Laura Duran", "Oficina y segundo piso",
     "«Nuestra experiencia con Ombu fue increíble.»",
     "Decidimos renovar completamente la oficina y hacer un segundo piso. Siempre nos sentimos acompañados en todo el proceso de renovación, desde escoger el diseño hasta los últimos detalles. ¡Definitivamente la mejor opción que pudimos hacer! ¡Increíble todo el proceso con ellos! Gracias Ombu 🙌🏻"),
    ("JJ", "Juan Miguel Jaramillo", "Cliente OMBU",
     "«Me fue muy bien.»",
     "Un proceso muy eficiente, los materiales excelentes y los acabados muy bonitos, todo muy rápido, muy buen presupuesto. Todo 100/100. Muy contento con el resultado."),
    ("SO", "Susana Ospina", "Remodelación completa de apartamento",
     "«Hice la remodelación completa de mi apartamento con Ombu. Fue la mejor decisión que pude haber tomado.»",
     "Ellos se encargaron de TODO. Yo solo tuve que soñar lo que quería y ellos lo hicieron realidad. Lo mejor de todo es que los materiales son de alta calidad. Los recomiendo 100%."),
]

# Proyectos (slugs de assets/js/proyectos.js). Los que no tienen fotos van como «pendiente».
DESTACADOS = ["torrealta", "fenikas", "aires-del-campestre", "palo-alto", "kuna-1002", "bosque-alto"]
REALIZADOS_SIN_FOTO = ["Tierra Clara", "Báltico", "Casa Mediterránea", "Twins", "Salento"]
TRANSFORMACIONES = ["torrealta", "fenikas", "aires-del-campestre", "palo-alto"]
OTROS = ["kuna-1002", "bosque-alto", "altos-de-la-rioja", "kuna-802", "altos-de-la-concha-2",
         "torrebalsillas", "palmar-de-la-abadia", "altos-de-la-concha"]

ICONOS_EXTRA = """    <symbol id="i-chev-d" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></g></symbol>
    <symbol id="i-link" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/></g></symbol>
    <symbol id="i-sofa" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 11V8a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v3"/><path d="M3 13a2 2 0 1 1 4 0v2h10v-2a2 2 0 1 1 4 0v4H3z"/><path d="M6 17v2M18 17v2"/></g></symbol>
    <symbol id="i-clipboard" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="4.5" width="14" height="16.5" rx="2"/><path d="M9 3h6v3H9z"/><path d="M9 13l2 2 4-4"/></g></symbol>
    <symbol id="i-camera" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></g></symbol>"""


# ---------------------------------------------------------------- utilidades

def R(n):
    """Rutas para una página a n carpetas de sitio/ (0 = sitio/, 1 = sitio/blog/, sitio/servicios/…)."""
    sube = "../" * n
    return {"A": "../" + sube + "assets/", "P": "../" + sube + "index.html", "u": lambda p: sube + p, "root": "../" + sube}


def esc(s):
    return html.escape(s, quote=True)


def jsonstr(s):
    return json.dumps(s, ensure_ascii=False)


def ico(i):
    return f'<svg aria-hidden="true"><use href="#{i}"/></svg>'


def sprite():
    with open(os.path.join(RAIZ, "herramientas", "iconos.svg.txt"), encoding="utf-8") as f:
        simbolos = f.read()
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">\n  <defs>\n'
            + simbolos + "\n" + ICONOS_EXTRA + "\n  </defs>\n</svg>")


def foto(slug, f, w, h, alt, n, sizes="(min-width: 960px) 560px, 100vw", lazy=True):
    A = R(n)["A"] + "img/proyectos/" + slug + "/"
    carga = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    return (f'<img src="{A}{f}-s.webp" srcset="{A}{f}-s.webp 768w, {A}{f}-l.webp {w}w" sizes="{sizes}" '
            f'width="{w}" height="{h}"{carga} alt="{esc(alt)}">')


def pendiente(texto, clase=""):
    return f'<div class="ph {clase}" role="img" aria-label="{esc(texto)}">{ico("i-camera")}<span>{texto}</span></div>'


# ---------------------------------------------------------------- partes comunes

def head(titulo, descripcion, n, og="website", extra=""):
    A = R(n)["A"]
    return f"""<!doctype html>
<html lang="es" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(titulo)}</title>
  <meta name="description" content="{esc(descripcion)}">
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#363840">
  <meta property="og:type" content="{og}">
  <meta property="og:locale" content="es_CO">
  <meta property="og:site_name" content="OMBU Renovaciones">
  <meta property="og:title" content="{esc(titulo)}">
  <meta property="og:description" content="{esc(descripcion)}">
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


def cabecera(n, activo):
    r = R(n)
    u = r["u"]
    cur = lambda k: ' aria-current="page"' if k == activo else ""
    svc_drop = "\n".join(
        f'              <li><a href="{u("servicios/" + s["slug"] + ".html")}"{cur("svc-" + s["slug"])}><span class="drop__ico">{ico(s["ico"])}</span>'
        f'<span><strong>{s["nombre"]}</strong>{s["resumen"]}</span></a></li>' for s in SERVICIOS)
    svc_menu = "\n".join(f'          <li><a href="{u("servicios/" + s["slug"] + ".html")}">{s["nombre"]}</a></li>' for s in SERVICIOS)
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
    <a class="btn btn--light btn--lg btn--block" href="{WA_COTIZAR}" target="_blank" rel="noopener">
      {ico("i-wa")} Escríbenos por WhatsApp
    </a>
    <div class="menu__social">
      <a href="https://www.instagram.com/ombu.renovaciones/" target="_blank" rel="noopener" aria-label="Instagram de OMBU">{ico("i-ig")}</a>
      <a href="https://www.facebook.com/share/1AA67nPHKe/" target="_blank" rel="noopener" aria-label="Facebook de OMBU">{ico("i-fb")}</a>
      <a class="menu__back" href="{r['P']}">← Volver a la propuesta</a>
    </div>
  </div>
</div>
"""


def pie(n):
    r = R(n)
    u = r["u"]
    links = "\n".join(f'        <li><a href="{u(p)}">{t}</a></li>' for k, t, p in MENU)
    return f"""<!-- ============ Pie ============ -->
<footer class="ftr on-dark">
  <div class="wrap ftr__grid">
    <div class="ftr__brand">
      <svg class="logo" viewBox="0 0 156 41" role="img" aria-label="OMBU"><use href="{r['A']}img/marca.svg#ombu-logo"/></svg>
      <p>Tú sueñas el espacio. <em>Nosotros nos encargamos de todo.</em></p>
    </div>
    <nav class="ftr__nav" aria-label="Pie de página">
      <ul>
{links}
      </ul>
    </nav>
    <div class="ftr__social">
      <p>Síguenos</p>
      <div>
        <a href="https://www.instagram.com/ombu.renovaciones/" target="_blank" rel="noopener" aria-label="Instagram de OMBU">{ico("i-ig")}</a>
        <a href="https://www.facebook.com/share/1AA67nPHKe/" target="_blank" rel="noopener" aria-label="Facebook de OMBU">{ico("i-fb")}</a>
        <a href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp de OMBU">{ico("i-wa")}</a>
      </div>
    </div>
  </div>
  <div class="wrap ftr__bottom">
    <p>© 2026 OMBU Renovaciones · Medellín, Antioquia</p>
    <p class="ftr__legal"><a href="{u(LEGAL)}">Política de datos</a><button type="button" data-cookies>Preferencias de cookies</button></p>
    <a href="{r['P']}">← Volver a la propuesta</a>
  </div>
</footer>
"""


def fab():
    return f"""<a class="fab" id="fab" href="{WA_COTIZAR}" target="_blank" rel="noopener" aria-label="Escríbenos por WhatsApp">
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
      <aside class="demo-note">
        <strong>Ficha del proyecto · pendiente</strong>
        Tipo de espacio, servicios realizados y una breve descripción. Se completa con la información que entregue OMBU para cada obra.
      </aside>
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


def pagina(titulo, desc, n, activo, pagina_id, cuerpo, js=(), og="website", extra_head="", extra_body=""):
    A = R(n)["A"]
    scripts = "\n".join(f'<script src="{A}js/{j}"></script>' for j in ("proyectos.js", "comun.js") + tuple(js))
    return (head(titulo, desc, n, og, extra_head)
            + f'<body data-page="{pagina_id}" data-root="{R(n)["root"]}">\n'
            + sprite() + '\n\n<a class="skip" href="#contenido">Saltar al contenido</a>\n\n' + cabecera(n, activo)
            + '\n<main id="contenido">\n' + cuerpo + '\n</main>\n\n' + pie(n) + fab() + extra_body
            + "\n" + scripts + "\n</body>\n</html>\n")


def phero(titulo, titulo_em, lead, migas, extra=""):
    """Encabezado de página interior. migas: [(texto, href|None)]"""
    m = '<span aria-hidden="true">/</span>'.join(
        f'<a href="{h}">{t}</a>' if h else f'<span aria-current="page">{t}</span>' for t, h in migas)
    return f"""  <section class="bhero" aria-labelledby="page-title">
    <div class="wrap">
      <nav class="crumbs" aria-label="Ruta">{m}</nav>
      <h1 class="display bhero__title" id="page-title">{titulo} <em>{titulo_em}</em></h1>
      <p class="lead">{lead}</p>{extra}
    </div>
  </section>
"""


# ---------------------------------------------------------------- secciones reutilizables

def sec_servicios(n, titulo, titulo_em, cta=True, excluir=None, eyebrow="Servicios"):
    u = R(n)["u"]
    cards = "\n".join(f"""        <li class="svc reveal">
          <a class="svc__link" href="{u('servicios/' + s['slug'] + '.html')}">
            <span class="svc__top"><span class="svc__ico">{ico(s['ico'])}</span><span class="svc__n" aria-hidden="true">{s['n']}</span></span>
            <h3 class="svc__name">{s['nombre']}</h3>
            <p>{s['resumen']}</p>
            <span class="svc__more">Ver servicio {ico('i-arrow')}</span>
          </a>
        </li>""" for s in SERVICIOS if s["slug"] != excluir)
    pie_ = f'\n      <a class="btn btn--lg sec__cta" href="{u("servicios/index.html")}">Conoce nuestros servicios {ico("i-arrow")}</a>' if cta else ""
    return f"""  <section class="sec svcs" id="servicios" aria-labelledby="svc-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">{eyebrow}</p>
        <h2 class="title" id="svc-title">{titulo} <em>{titulo_em}</em></h2>
      </div>
      <ul class="svc__grid" role="list">
{cards}
      </ul>{pie_}
    </div>
  </section>
"""


def sec_por_que(n, titulo, titulo_em, eyebrow="Por qué elegirnos"):
    cards = "\n".join(f"""        <li class="why__card reveal">
          <span class="why__ico">{ico(i)}</span>
          <h3>{t}</h3>
          <p>{d}</p>
        </li>""" for i, t, d in ATRIBUTOS)
    return f"""  <section class="sec why on-dark" id="por-que" aria-labelledby="why-title">
    <svg class="why__ring" viewBox="0 0 2250 2250" aria-hidden="true"><use href="{R(n)['A']}img/marca.svg#ombu-mark"/></svg>
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">{eyebrow}</p>
        <h2 class="title" id="why-title">{titulo} <em>{titulo_em}</em></h2>
      </div>
      <ul class="why__grid why__grid--5" role="list">
{cards}
      </ul>
    </div>
  </section>
"""


def sec_pasos(n):
    u = R(n)["u"]
    pasos = "\n".join(f"""        <li class="step reveal">
          <span class="step__n" aria-hidden="true">0{i}</span>
          <span class="step__ico">{ico(ic)}</span>
          <h3>{t}</h3>
          <p>{d}</p>
        </li>""" for i, (ic, t, d) in enumerate(PASOS, 1))
    return f"""  <section class="sec process" id="proceso" aria-labelledby="process-title">
    <div class="wrap process__grid">
      <div class="process__intro reveal">
        <p class="eyebrow">Cómo trabajamos</p>
        <h2 class="title" id="process-title">Un solo equipo. <em>Un proceso pensado para ti.</em></h2>
        <p class="lead">De la primera conversación a la entrega final, te acompañamos en cada decisión.</p>
        <a class="btn btn--lg process__cta" href="{u('nosotros.html#proceso')}">Conoce nuestro proceso {ico('i-arrow')}</a>
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


def sec_testimonios():
    items = "\n".join(f"""        <li class="quote">
          <svg class="quote__mark" aria-hidden="true"><use href="#i-quote"/></svg>
          <p class="quote__lead">{lead}</p>
          <p class="quote__text">{txt}</p>
          <p class="quote__who"><span class="quote__avatar" aria-hidden="true">{ini}</span><span><strong>{nom}</strong> {det}</span></p>
        </li>""" for ini, nom, det, lead, txt in TESTIMONIOS)
    return f"""  <section class="sec quotes" id="testimonios" aria-labelledby="quotes-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">Testimonios</p>
        <h2 class="title" id="quotes-title">Ellos ya confiaron <em>en OMBU</em></h2>
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
    items = "\n".join(f"""        <details class="faq__item">
          <summary>{q}<svg class="chev" aria-hidden="true"><use href="#i-chev-d"/></svg></summary>
          <p>{a}</p>
        </details>""" for q, a in FAQ)
    mas = f'\n        <p class="faq__more">¿Tienes otra pregunta? <a href="{R(n)["u"]("contacto.html")}">Escríbenos</a></p>' if enlace else ""
    return f"""  <section class="sec faq" id="preguntas" aria-labelledby="faq-title">
    <div class="wrap faq__grid">
      <div class="sec__head reveal">
        <p class="eyebrow">Preguntas frecuentes</p>
        <h2 class="title" id="faq-title">Lo que más <em>nos preguntan</em></h2>{mas}
      </div>
      <div class="faq__list reveal">
{items}
      </div>
    </div>
  </section>
"""


def banda(n, titulo, titulo_em, texto, cta, href="contacto.html"):
    return f"""  <section class="band on-dark" aria-labelledby="band-title">
    <picture class="band__media" aria-hidden="true">
      <img src="{R(n)['A']}img/proyectos/palo-alto/d01-s.webp" width="768" height="512" loading="lazy" decoding="async" alt="">
    </picture>
    <div class="wrap band__in reveal">
      <h2 class="band__title display" id="band-title">{titulo} <em>{titulo_em}</em></h2>
      <p class="lead">{texto}</p>
      <a class="btn btn--light btn--lg" href="{R(n)['u'](href)}">{cta} {ico('i-arrow')}</a>
    </div>
  </section>
"""


def tarjeta(a, n, cabeza="h3"):
    r = R(n)
    href = r["u"]("blog/" + a["slug"] + ".html")
    w, h = 768, round(768 * a["portada"][2] / a["portada"][1])
    return f"""<li class="post" data-cat="{a['categoria']}">
  <a class="post__link" href="{href}">
    <div class="post__media"><img src="{r['A']}img/{a['portada_s']}" width="{w}" height="{h}" loading="lazy" decoding="async" alt=""></div>
    <div class="post__body">
      <p class="post__meta"><span class="post__cat">{a['categoria']}</span><span>{a['lectura']} min de lectura</span></p>
      <{cabeza} class="post__title">{a['titulo']} <em>{a['titulo_em']}</em></{cabeza}>
      <p class="post__excerpt">{a['resumen']}</p>
      <span class="post__more">Leer artículo {ico('i-arrow')}</span>
    </div>
  </a>
</li>"""


def sec_blog(n, titulo="Ideas para", titulo_em="tu próximo espacio", lista=None, eyebrow="Blog"):
    lista = lista if lista is not None else ARTICULOS[:3]
    t = "\n".join(tarjeta(a, n) for a in lista)
    return f"""  <section class="sec blog-teaser" aria-labelledby="bt-title">
    <div class="wrap">
      <div class="sec__head bt__head reveal">
        <div>
          <p class="eyebrow">{eyebrow}</p>
          <h2 class="title" id="bt-title">{titulo} <em>{titulo_em}</em></h2>
        </div>
        <a class="link-arrow" href="{R(n)['u']('blog/index.html')}">Ver todo el blog {ico('i-arrow')}</a>
      </div>
    </div>
    <div class="rail rail--posts" data-rail>
      <ul class="rail__track" role="list" tabindex="0" aria-label="Artículos del blog. Desliza para ver más.">
{t}
      </ul>
    </div>
  </section>
"""


def banda_final(n, cta="Hablemos de tu proyecto", href="contacto.html"):
    return banda(n, "Tu próximo espacio empieza", "con una conversación.",
                 "Cuéntanos qué tienes en mente. Nuestro equipo te ayudará a dar el primer paso.", cta, href)


# ---------------------------------------------------------------- páginas

def pag_inicio():
    A = R(0)["A"]
    preload = f"""  <link rel="preload" as="image" href="{A}img/hero-768.webp"
        imagesrcset="{A}img/hero-768.webp 768w, {A}img/hero-1024.webp 1024w, {A}img/hero-1536.webp 1536w, {A}img/hero-1920.webp 1920w"
        imagesizes="100vw">
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"GeneralContractor","name":"OMBU Renovaciones","url":"https://omburenovaciones.com/",
   "logo":"{URL}assets/img/icon-512.png","image":"{URL}assets/img/og-sitio.jpg",
   "description":"Diseño y construcción para transformar viviendas, oficinas y espacios comerciales.",
   "telephone":"+57 310 599 6809","areaServed":"Medellín, Antioquia",
   "address":{{"@type":"PostalAddress","addressLocality":"Medellín","addressRegion":"Antioquia","addressCountry":"CO"}},
   "sameAs":["https://www.instagram.com/ombu.renovaciones/","https://www.facebook.com/share/1AA67nPHKe/"]}}
  </script>
"""
    cuerpo = f"""
  <!-- ============ Hero ============ -->
  <section class="hero on-dark" id="inicio" aria-labelledby="hero-title">
    <picture class="hero__media">
      <img src="{A}img/hero-768.webp"
           srcset="{A}img/hero-768.webp 768w, {A}img/hero-1024.webp 1024w, {A}img/hero-1536.webp 1536w, {A}img/hero-1920.webp 1920w"
           sizes="100vw" width="1920" height="1280" fetchpriority="high"
           alt="Sala y cocina renovadas por OMBU con paneles de madera, piso laminado y ventanales hacia la naturaleza">
    </picture>
    <div class="hero__body wrap">
      <p class="eyebrow">Diseño y construcción · Medellín</p>
      <h1 class="hero__title display" id="hero-title">Tú sueñas el espacio. <em>Nosotros nos encargamos de todo.</em></h1>
      <p class="hero__lead">Diseñamos, transformamos y construimos espacios que se adaptan a ti. Con un equipo propio que te acompaña desde la primera idea hasta la entrega final.</p>
      <div class="hero__ctas">
        <a class="btn btn--light btn--lg" href="contacto.html">Empezar mi proyecto {ico('i-arrow')}</a>
        <a class="btn btn--ghost btn--lg" href="proyectos.html">Ver proyectos</a>
      </div>
      <ul class="hero__trust" aria-label="Garantías">
        <li>{ico('i-check')} Equipo propio</li>
        <li>{ico('i-check')} Presupuestos cerrados</li>
        <li>{ico('i-check')} Primera reunión gratis</li>
      </ul>
    </div>
  </section>

  <!-- ============ Sobre OMBU ============ -->
  <section class="sec story" aria-labelledby="story-title">
    <div class="wrap story__grid">
      <figure class="story__media reveal">
        <img src="{A}img/fondo-768.webp"
             srcset="{A}img/fondo-768.webp 768w, {A}img/fondo-1024.webp 1024w, {A}img/fondo-1536.webp 1536w"
             sizes="(min-width: 960px) 560px, 100vw" width="1536" height="1024" loading="lazy" decoding="async"
             alt="Sala renovada con muro revestido en madera, sofá claro y comedor al fondo">
        <div class="story__badge" aria-hidden="true">
          <svg viewBox="0 0 2250 2250"><use href="{A}img/marca.svg#ombu-mark"/></svg>
        </div>
      </figure>
      <div class="story__copy reveal">
        <p class="eyebrow">Sobre OMBU</p>
        <h2 class="title" id="story-title">Espacios pensados para ti. <em>Procesos respaldados por expertos.</em></h2>
        <p>Somos una empresa de diseño y construcción especializada en transformar viviendas, oficinas y espacios comerciales.</p>
        <p>Creemos que cada espacio debe responder a quienes lo habitan. Por eso, combinamos <strong>diseño personalizado, conocimiento técnico y un equipo propio</strong> de profesionales para hacer realidad cada proyecto.</p>
        <a class="btn btn--lg story__cta" href="nosotros.html">Conoce OMBU {ico('i-arrow')}</a>
      </div>
    </div>
  </section>

{sec_servicios(0, "Todo lo que necesitas", "para transformar tu espacio.", eyebrow="Nuestros servicios")}
{sec_pasos(0)}
  <!-- ============ Proyectos destacados ============ -->
  <section class="sec projects" id="proyectos" aria-labelledby="projects-title">
    <div class="wrap">
      <div class="sec__head projects__head reveal">
        <div>
          <p class="eyebrow">Proyectos destacados</p>
          <h2 class="title" id="projects-title">Los espacios cuentan <em>nuestra historia.</em></h2>
        </div>
        <div class="badge" aria-hidden="true"><strong>+80</strong><span>proyectos</span></div>
      </div>
      <p class="lead projects__lead reveal">Cada proyecto es una oportunidad para transformar ideas en espacios reales. Explora algunos de nuestros trabajos. <span class="sr-only">Más de 80 proyectos realizados.</span></p>
    </div>
{carril(DESTACADOS, "Proyectos destacados")}
    <div class="wrap"><a class="btn btn--lg sec__cta" href="proyectos.html">Ver todos los proyectos {ico('i-arrow')}</a></div>
  </section>

{sec_por_que(0, "La tranquilidad de estar", "en buenas manos.", "¿Por qué elegir OMBU?")}
{sec_testimonios()}
{sec_faq(0, enlace=True)}
{sec_blog(0)}
{banda_final(0)}"""
    return pagina("OMBU Renovaciones · Diseño y construcción de espacios en Medellín",
                  "Diseñamos, transformamos y construimos viviendas, oficinas y espacios comerciales en Medellín, con un equipo propio de la primera idea a la entrega.",
                  0, "inicio", "inicio", cuerpo, js=("inicio.js",), extra_head=preload, extra_body=dialogos())


def pag_nosotros():
    A = R(0)["A"]
    etapas, k = [], 0
    for i, (t, pasos) in enumerate(ETAPAS, 1):
        items = "".join(f'<li value="{k + j}">{p}</li>' for j, p in enumerate(pasos, 1))
        k += len(pasos)
        etapas.append(f"""        <li class="stage reveal">
          <p class="stage__n">Etapa {i}</p>
          <h3 class="stage__title">{t}</h3>
          <ol class="stage__list">{items}</ol>
        </li>""")
    equipo = "\n".join(f"        <li>{pendiente('Foto pendiente: ' + t)}<p>{t}</p></li>" for t in ("Reuniones de diseño", "Visitas de obra", "Ejecución"))
    nl = "\n"
    cuerpo = phero("Diseñamos espacios.", "Construimos confianza.",
                   "En OMBU creemos que un espacio bien pensado puede transformar la manera en que vivimos y trabajamos.",
                   [("Inicio", "index.html"), ("Nosotros", None)]) + f"""
  <section class="sec story" aria-labelledby="who-title">
    <div class="wrap story__grid">
      <figure class="story__media reveal">
        <img src="{A}img/fondo-768.webp"
             srcset="{A}img/fondo-768.webp 768w, {A}img/fondo-1024.webp 1024w, {A}img/fondo-1536.webp 1536w"
             sizes="(min-width: 960px) 560px, 100vw" width="1536" height="1024" loading="lazy" decoding="async"
             alt="Sala renovada por OMBU con muro revestido en madera">
        <div class="story__badge" aria-hidden="true">
          <svg viewBox="0 0 2250 2250"><use href="{A}img/marca.svg#ombu-mark"/></svg>
        </div>
      </figure>
      <div class="story__copy reveal">
        <p class="eyebrow">Quiénes somos</p>
        <h2 class="title" id="who-title">Un solo equipo, <em>de la idea a la entrega.</em></h2>
        <p>Somos una empresa de diseño y construcción enfocada en renovar viviendas, oficinas y locales comerciales para convertirlos en espacios funcionales, personalizados y alineados con las necesidades de cada cliente.</p>
        <p>Contamos con un <strong>equipo propio de diseño, interiorismo, construcción, mano de obra y logística.</strong> Esto nos permite mantener el control del proceso y ofrecer acompañamiento desde el inicio hasta la entrega.</p>
      </div>
    </div>
  </section>

{sec_por_que(0, "Lo que nos", "diferencia.")}
  <!-- ============ Cómo trabajamos ============ -->
  <section class="sec stages" id="proceso" aria-labelledby="stages-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">Cómo trabajamos</p>
        <h2 class="title" id="stages-title">De una idea a un espacio <em>hecho realidad.</em></h2>
        <p class="lead">Creemos en procesos claros, comunicación cercana y decisiones bien acompañadas. Así transformamos tu proyecto paso a paso.</p>
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
        <p class="eyebrow">Nuestro equipo</p>
        <h2 class="title" id="team-title">Detrás de cada espacio, <em>hay un equipo.</em></h2>
        <p class="lead">Diseñadores, profesionales de construcción y personal operativo trabajan de manera coordinada para que cada etapa del proyecto avance bajo una misma visión.</p>
      </div>
      <ul class="team__grid reveal" role="list">
{equipo}
      </ul>
    </div>
  </section>

{banda_final(0, "Quiero empezar mi proyecto")}"""
    return pagina("Nosotros · OMBU Renovaciones", "Somos una empresa de diseño y construcción con equipo propio. Conoce quiénes somos y cómo trabajamos.",
                  0, "nosotros", "nosotros", cuerpo)


def pag_servicios():
    cuerpo = (phero("Soluciones integrales", "para cada espacio.",
                    "Diseño, construcción, mobiliario e interventoría con un mismo equipo. Elige por dónde empezar o combínalos en un solo proyecto.",
                    [("Inicio", "../index.html"), ("Servicios", None)])
              + sec_servicios(1, "Todo lo que necesitas", "para transformar tu espacio.", cta=False)
              + sec_pasos(1) + sec_faq(1, enlace=True) + banda_final(1))
    return pagina("Servicios · OMBU Renovaciones", "Diseño, construcción, mobiliario e interventoría para viviendas, oficinas y espacios comerciales en Medellín.",
                  1, "servicios", "servicios", cuerpo)


def pag_servicio(s):
    slug, f, w, h = s["foto"]
    lista = "\n".join(f"        <li>{ico('i-check')}<span>{x}</span></li>" for x in s["lista"])
    catalogo = ""
    if s["slug"] == "mobiliario":
        piezas = "\n".join(f"        <li>{pendiente('Foto pendiente', 'ph--sq')}<p>Pieza {i} · por confirmar</p></li>" for i in range(1, 7))
        catalogo = f"""
  <section class="sec catalog" aria-labelledby="cat-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">Catálogo</p>
        <h2 class="title" id="cat-title">Piezas exclusivas <em>para tu espacio.</em></h2>
        <p class="lead">Entre 10 y 15 productos exclusivos, además de opciones personalizadas. Las fotos y referencias del catálogo están pendientes.</p>
      </div>
      <ul class="team__grid team__grid--3" role="list">
{piezas}
      </ul>
    </div>
  </section>
"""
    cta = f"contacto.html?servicio={quote(s['nombre'])}"
    cuerpo = f"""  <section class="shero" aria-labelledby="page-title">
    <div class="wrap shero__grid">
      <div class="shero__copy">
        <nav class="crumbs" aria-label="Ruta"><a href="../index.html">Inicio</a><span aria-hidden="true">/</span><a href="index.html">Servicios</a><span aria-hidden="true">/</span><span aria-current="page">{s['nombre']}</span></nav>
        <p class="eyebrow">{s['n']} · {s['nombre']}</p>
        <h1 class="display shero__title" id="page-title">{s['titulo']} <em>{s['titulo_em']}</em></h1>
        <p class="lead">{s['texto']}</p>
        <a class="btn btn--lg shero__cta" href="../{cta}">{s['cta']} {ico('i-arrow')}</a>
      </div>
      <figure class="shero__media">{foto(slug, f, w, h, 'Proyecto de OMBU', 1, lazy=False)}</figure>
    </div>
  </section>

  <section class="sec incl" aria-labelledby="incl-title">
    <div class="wrap incl__grid">
      <div class="sec__head reveal">
        <span class="svc__ico svc__ico--lg">{ico(s['ico'])}</span>
        <h2 class="title" id="incl-title">{s['lista_titulo']}</h2>
      </div>
      <ul class="incl__list reveal" role="list">
{lista}
      </ul>
    </div>
  </section>
{catalogo}
{sec_servicios(1, "Otros servicios", "que se complementan.", cta=False, excluir=s['slug'], eyebrow="También hacemos")}
{banda_final(1, s['cta'], cta)}"""
    return pagina(f"{s['nombre']} · Servicios OMBU Renovaciones", s["texto"], 1, "svc-" + s["slug"], "servicio", cuerpo)


def pag_proyectos():
    def ph_card(nombre, nota):
        return f"""        <li class="card card--ph">{pendiente(nota + ': ' + nombre, 'ph--cmp')}
          <p class="card__btn"><span class="card__txt"><span class="card__name">{nombre}</span><span class="card__meta">{nota}</span></span></p>
        </li>"""

    def sec(id_, eyebrow, titulo, titulo_em, lead, ul):
        return f"""  <section class="sec projects pgal" id="{id_}" aria-labelledby="{id_}-title">
    <div class="wrap">
      <div class="sec__head reveal">
        <p class="eyebrow">{eyebrow}</p>
        <h2 class="title" id="{id_}-title">{titulo} <em>{titulo_em}</em></h2>
        <p class="lead">{lead}</p>
      </div>
{ul}
    </div>
  </section>
"""
    realizados = "\n".join(ph_card(t, "Fotos pendientes") for t in REALIZADOS_SIN_FOTO)
    badge = '\n      <div class="badge bhero__badge" aria-hidden="true"><strong>+80</strong><span>proyectos</span></div>'
    cuerpo = (phero("Espacios que hablan", "por nosotros.",
                    'Detrás de cada proyecto hay una idea, un proceso y una transformación. Conoce algunos de los espacios que hemos diseñado y construido. <span class="sr-only">Más de 80 proyectos.</span>',
                    [("Inicio", "index.html"), ("Proyectos", None)], badge)
              + sec("realizados", "Galería 1", "Proyectos", "realizados.", "El resultado final de algunos de nuestros proyectos.",
                    f'      <ul class="pgrid" role="list">\n{realizados}\n      </ul>')
              + sec("transformaciones", "Galería 2", "Transformaciones:", "antes y después.",
                    "Desliza cada foto para comparar el espacio antes y después de la obra. Toca el nombre para ver todas las fotos.",
                    f'      <ul class="pgrid" data-proj="{",".join(TRANSFORMACIONES)}" role="list">\n{ph_card("Salento", "Antes y después pendiente")}\n      </ul>')
              + sec("mas", "Más proyectos", "Otros espacios", "que transformamos.", "Más obras de OMBU con fotos del antes y el después.",
                    f'      <ul class="pgrid" data-proj="{",".join(OTROS)}" role="list"></ul>')
              + banda_final(0, "Quiero transformar mi espacio"))
    return pagina("Proyectos · OMBU Renovaciones", "Más de 80 proyectos de diseño y construcción. Mira el antes y el después de las obras de OMBU.",
                  0, "proyectos", "proyectos", cuerpo, js=("inicio.js",), extra_body=dialogos())


def pag_contacto():
    chips = "\n".join(f'            <label class="chip"><input type="radio" name="espacio" value="{v}"{" checked" if i == 0 else ""}><span>{v}</span></label>'
                      for i, v in enumerate(["Vivienda", "Oficina", "Local comercial", "Otro"]))

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
        <h1 class="display bhero__title" id="page-title">Hablemos del espacio <em>que tienes en mente.</em></h1>
        <p class="lead">Toda transformación comienza con una idea. Cuéntanos la tuya y nuestro equipo se pondrá en contacto contigo.</p>
        <ul class="channels" role="list">
          <li><a class="channel" href="{WA}" target="_blank" rel="noopener"><span class="channel__ico">{ico('i-wa')}</span><span><small>WhatsApp</small>+57 310 599 6809</span></a></li>
          <li><a class="channel" href="https://www.instagram.com/ombu.renovaciones/" target="_blank" rel="noopener"><span class="channel__ico">{ico('i-ig')}</span><span><small>Instagram</small>@ombu.renovaciones</span></a></li>
          <li><div class="channel"><span class="channel__ico">{ico('i-pin')}</span><span><small>Ubicación</small>Medellín, Antioquia</span></div></li>
        </ul>
      </div>

      <div class="form-wrap">
        <form class="form" id="form" novalidate>
          <h2 class="form__title">Cuéntanos de tu proyecto</h2>
          <p class="form__hint">Toma menos de un minuto.</p>
          <div class="form__row">
{campo("name", "nombre", "Nombre", "text", "given-name")}
{campo("last", "apellido", "Apellido", "text", "family-name")}
          </div>
          <div class="form__row">
{campo("phone", "celular", "Celular", "tel", "tel", ' inputmode="tel" placeholder="300 123 4567"')}
{campo("city", "ciudad", "Ciudad", "text", "address-level2", ' placeholder="Medellín"')}
          </div>
          <fieldset class="field">
            <legend>¿Qué espacio quieres transformar?</legend>
            <div class="chips">
{chips}
            </div>
          </fieldset>
          <div class="field">
            <label for="f-msg">Cuéntanos tu idea <span class="field__opt">(opcional)</span></label>
            <textarea id="f-msg" name="mensaje" rows="4" placeholder="Ej.: renovar cocina y baños, cambiar pisos…"></textarea>
          </div>
          <div class="field">
            <label class="check"><input id="f-ok" type="checkbox" name="autorizo" required aria-describedby="e-ok"><span>Autorizo a OMBU Renovaciones a tratar mis datos personales según su <a href="{LEGAL}" target="_blank">política de tratamiento de datos</a>.</span></label>
            <p class="field__err" id="e-ok" aria-live="polite"></p>
          </div>
          <button class="btn btn--lg btn--block form__submit" type="submit">Enviar mi proyecto {ico('i-arrow')}</button>
          <p class="form__note">Se abrirá WhatsApp con tu mensaje listo para enviar.</p>
        </form>
        <div class="form form--ok" id="form-ok" tabindex="-1" hidden>
          <span class="form__ok-ico">{ico('i-check')}</span>
          <h2 class="form__title">¡Gracias por compartir tu idea!</h2>
          <p>Recibimos tu información y nuestro equipo se pondrá en contacto contigo.</p>
          <p class="form__note">¿No se abrió WhatsApp? <a id="form-wa" href="{WA}" target="_blank" rel="noopener">Envía tu mensaje aquí</a>.</p>
        </div>
      </div>
    </div>
  </section>

{sec_faq(0)}"""
    return pagina("Contacto · OMBU Renovaciones", "Cuéntanos tu idea y nuestro equipo se pondrá en contacto contigo. La primera reunión es gratuita.",
                  0, "contacto", "contacto", cuerpo, js=("inicio.js",))


def pag_blog_indice():
    d = ARTICULOS[0]
    resto = "\n".join(tarjeta(a, 1) for a in ARTICULOS[1:])
    cats = sorted({a["categoria"] for a in ARTICULOS})
    chips = "\n".join(f'          <button class="filter" type="button" aria-pressed="false" data-filter="{c}">{c}</button>' for c in cats)
    cuerpo = phero("Ideas, inspiración y conocimiento", "para transformar espacios.",
                   "Diseño e interiorismo, consejos para renovar, materiales, procesos de construcción y tendencias.",
                   [("Inicio", "../index.html"), ("Blog", None)]) + f"""
  <section class="wrap blist" aria-label="Artículos">
    <article class="feature reveal" data-cat="{d['categoria']}">
      <a class="feature__link" href="{d['slug']}.html">
        <div class="feature__media"><img src="../../assets/img/{d['portada'][0]}" width="{d['portada'][1]}" height="{d['portada'][2]}" alt="{d['portada_alt']}" fetchpriority="high"></div>
        <div class="feature__body">
          <p class="post__meta"><span class="post__cat">{d['categoria']}</span><span>{d['fecha_txt']}</span><span>{d['lectura']} min</span></p>
          <h2 class="feature__title">{d['titulo']} <em>{d['titulo_em']}</em></h2>
          <p class="post__excerpt">{d['resumen']}</p>
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

""" + banda_final(1)
    return pagina("Blog · OMBU Renovaciones", "Ideas, inspiración y conocimiento para transformar espacios: diseño, renovación, materiales y construcción.",
                  1, "blog", "blog", cuerpo, js=("blog.js",))


def pag_articulo(a):
    otros = [x for x in ARTICULOS if x["slug"] != a["slug"]]
    cuerpo_art = a["cuerpo"].replace("{A}", "../../assets/")
    titulo_txt = f'{a["titulo"]} {a["titulo_em"]}'
    ld = f"""  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BlogPosting","headline":{jsonstr(titulo_txt)},"description":{jsonstr(a['resumen'])},
   "datePublished":"{a['fecha']}","image":"{URL}assets/img/{a['portada'][0]}","author":{{"@type":"Organization","name":"OMBU Renovaciones"}},
   "publisher":{{"@type":"Organization","name":"OMBU Renovaciones","logo":{{"@type":"ImageObject","url":"{URL}assets/img/icon-512.png"}}}}}}
  </script>
"""
    share = quote(f"{titulo_txt} · OMBU Renovaciones")
    cuerpo = f"""  <article class="art">
    <header class="art__head wrap">
      <nav class="crumbs" aria-label="Ruta"><a href="../index.html">Inicio</a><span aria-hidden="true">/</span><a href="index.html">Blog</a><span aria-hidden="true">/</span><span aria-current="page">{a['categoria']}</span></nav>
      <p class="post__meta"><span class="post__cat">{a['categoria']}</span><span><time datetime="{a['fecha']}">{a['fecha_txt']}</time></span><span>{a['lectura']} min de lectura</span></p>
      <h1 class="display art__title">{a['titulo']} <em>{a['titulo_em']}</em></h1>
      <p class="lead art__lead">{a['resumen']}</p>
      <p class="art__by"><span class="art__avatar" aria-hidden="true"><svg viewBox="0 0 2250 2250"><use href="../../assets/img/marca.svg#ombu-mark"/></svg></span><span><strong>Equipo OMBU</strong>Diseño y construcción</span></p>
    </header>
    <figure class="art__cover wrap">
      <img src="../../assets/img/{a['portada'][0]}" width="{a['portada'][1]}" height="{a['portada'][2]}" alt="{a['portada_alt']}" fetchpriority="high">
      <figcaption>{a['pie_portada']}</figcaption>
    </figure>
    <div class="art__layout wrap">
      <div class="prose">
{cuerpo_art}
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
        <svg class="cta-box__mark" viewBox="0 0 2250 2250" aria-hidden="true"><use href="../../assets/img/marca.svg#ombu-mark"/></svg>
        <h2 class="cta-box__title" id="cta-title">¿Quieres transformar <em>tu espacio?</em></h2>
        <p>Cuéntanos qué tienes en mente. La primera reunión es gratuita.</p>
        <div class="cta-box__btns">
          <a class="btn btn--light btn--lg" href="../contacto.html">Empezar mi proyecto {ico('i-arrow')}</a>
          <a class="btn btn--ghost btn--lg" href="{WA_COTIZAR}" target="_blank" rel="noopener">{ico('i-wa')} WhatsApp</a>
        </div>
      </div>
    </section>
  </article>

{sec_blog(1, "Más ideas", "del blog", otros, "Sigue leyendo")}"""
    return pagina(f"{titulo_txt} · Blog OMBU", a["resumen"], 1, "blog", "articulo", cuerpo, js=("blog.js",), og="article", extra_head=ld)


PEND = '<mark class="pend">por confirmar</mark>'


def pag_politica():
    cuerpo = f"""  <article class="art legal">
    <header class="art__head wrap">
      <nav class="crumbs" aria-label="Ruta"><a href="../index.html">Inicio</a><span aria-hidden="true">/</span><span aria-current="page">Política de datos</span></nav>
      <h1 class="display art__title">Política de tratamiento <em>de datos personales</em></h1>
      <p class="lead art__lead">Cómo recolectamos, usamos y protegemos tu información, y cómo puedes conocerla, actualizarla o pedir que la eliminemos.</p>
      <p class="post__meta"><span>Vigente desde el 19 de octubre de 2026</span></p>
    </header>
    <div class="wrap legal__body">
      <div class="prose">
        <h2>1. Responsable del tratamiento</h2>
        <ul>
          <li><strong>Responsable:</strong> OMBU Renovaciones</li>
          <li><strong>NIT:</strong> {PEND}</li>
          <li><strong>Domicilio:</strong> Medellín, Antioquia, Colombia. Dirección: {PEND}</li>
          <li><strong>Correo para temas de datos:</strong> {PEND}</li>
          <li><strong>WhatsApp:</strong> <a href="{WA}" target="_blank" rel="noopener">+57 310 599 6809</a></li>
        </ul>

        <h2>2. Marco legal</h2>
        <p>Esta política cumple la Ley Estatutaria 1581 de 2012, el Decreto 1377 de 2013 (compilado en el Decreto Único 1074 de 2015) y demás normas colombianas sobre protección de datos personales.</p>

        <h2>3. Qué datos recolectamos</h2>
        <ul>
          <li><strong>Datos de contacto:</strong> nombre, apellido, número de celular y ciudad que escribes en el formulario o nos envías por WhatsApp.</li>
          <li><strong>Datos del proyecto:</strong> tipo de espacio, ideas, fotos, planos y medidas que decidas compartir.</li>
          <li><strong>Datos de navegación:</strong> tus preferencias de cookies, guardadas en tu propio navegador.</li>
        </ul>
        <p>No pedimos datos sensibles ni datos de menores de edad.</p>

        <h2>4. Para qué los usamos</h2>
        <ul>
          <li>Responder tu solicitud, asesorarte y preparar tu cotización.</li>
          <li>Coordinar visitas, diseño, ejecución y entrega de tu proyecto.</li>
          <li>Enviarte información sobre el estado de tu obra y garantías.</li>
          <li>Enviarte novedades de OMBU, solo si nos das permiso. Puedes retirarlo cuando quieras.</li>
          <li>Cumplir obligaciones legales, contables y tributarias.</li>
        </ul>

        <h2>5. Autorización</h2>
        <p>Al marcar la casilla de autorización del formulario, o al escribirnos por WhatsApp, nos autorizas a tratar tus datos para las finalidades anteriores. Guardamos prueba de esa autorización mientras dure la relación contigo.</p>

        <h2>6. Tus derechos</h2>
        <p>Como titular de los datos puedes:</p>
        <ul>
          <li>Conocer, actualizar y corregir tus datos.</li>
          <li>Pedir prueba de la autorización que nos diste.</li>
          <li>Saber cómo hemos usado tus datos.</li>
          <li>Revocar la autorización o pedir que eliminemos tus datos, cuando no exista un deber legal o contractual de conservarlos.</li>
          <li>Presentar quejas ante la Superintendencia de Industria y Comercio (SIC).</li>
          <li>Acceder gratis a tus datos personales.</li>
        </ul>

        <h2>7. Cómo ejercer tus derechos</h2>
        <p>Escríbenos al correo de datos o por WhatsApp con tu nombre, número de contacto y lo que necesitas.</p>
        <ul>
          <li><strong>Consultas:</strong> respondemos en máximo 10 días hábiles. Si necesitamos más tiempo te avisamos, y nunca serán más de 5 días hábiles adicionales.</li>
          <li><strong>Reclamos</strong> (corrección, actualización, eliminación o revocatoria): respondemos en máximo 15 días hábiles, prorrogables hasta 8 días hábiles más con aviso previo.</li>
        </ul>
        <p>Antes de acudir a la SIC debes haber presentado tu consulta o reclamo ante nosotros.</p>

        <h2>8. Con quién compartimos tus datos</h2>
        <p>No vendemos ni alquilamos tus datos. Los compartimos solo con quienes nos ayudan a prestar el servicio (por ejemplo, proveedores y contratistas de tu obra) y bajo deber de confidencialidad. Las conversaciones por WhatsApp pasan por los servidores de Meta Platforms, que pueden estar fuera de Colombia.</p>

        <h2>9. Seguridad y conservación</h2>
        <p>Aplicamos medidas razonables para evitar pérdida, uso o acceso no autorizado a tus datos. Los conservamos mientras dure la relación contigo y el tiempo que exija la ley.</p>

        <h2 id="cookies">10. Cookies</h2>
        <p>Las cookies son pequeños archivos que el sitio guarda en tu navegador. Las agrupamos así:</p>
        <ul>
          <li><strong>Necesarias:</strong> hacen funcionar el sitio y recuerdan tus preferencias de cookies. Siempre están activas.</li>
          <li><strong>Analítica:</strong> nos dirían qué páginas se visitan para mejorar el sitio. Solo se activan si las aceptas.</li>
          <li><strong>Marketing:</strong> permitirían mostrarte anuncios de OMBU en otras plataformas. Solo se activan si las aceptas.</li>
        </ul>
        <p>Hoy este sitio solo usa las necesarias. Puedes cambiar tu elección cuando quieras:</p>
        <p><button class="btn" type="button" data-cookies>Preferencias de cookies</button></p>

        <h2>11. Cambios a esta política</h2>
        <p>Si cambiamos esta política publicaremos la nueva versión en esta página con su fecha de vigencia. Si el cambio afecta las finalidades, te pediremos una nueva autorización.</p>
      </div>
    </div>
  </article>
"""
    return pagina("Política de tratamiento de datos · OMBU Renovaciones", "Cómo OMBU Renovaciones recolecta, usa y protege tus datos personales, y cómo ejercer tus derechos.",
                  1, "", "legal", cuerpo)


# ---------------------------------------------------------------- escritura

def main():
    paginas = {
        "index.html": pag_inicio(),
        "nosotros.html": pag_nosotros(),
        "proyectos.html": pag_proyectos(),
        "contacto.html": pag_contacto(),
        "servicios/index.html": pag_servicios(),
        "blog/index.html": pag_blog_indice(),
        LEGAL: pag_politica(),
    }
    for s in SERVICIOS:
        paginas["servicios/" + s["slug"] + ".html"] = pag_servicio(s)
    for a in ARTICULOS:
        paginas["blog/" + a["slug"] + ".html"] = pag_articulo(a)
    for ruta, contenido in paginas.items():
        ruta = os.path.join(SITIO, ruta)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
    print("Generadas", len(paginas), "páginas en sitio/")


if __name__ == "__main__":
    main()
