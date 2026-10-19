# -*- coding: utf-8 -*-
"""Genera las partes comunes del sitio y las páginas del blog.

    python3 herramientas/generar.py

- Rellena en sitio/index.html las zonas marcadas <!-- @nombre --> … <!-- /@nombre -->
  (iconos, cabecera, pie y avance del blog).
- Escribe sitio/blog/index.html y una página por artículo (herramientas/articulos.py).

Así la cabecera, el menú y el pie son idénticos en todas las páginas.
"""
import os
import re
import html

from articulos import ARTICULOS

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITIO = os.path.join(RAIZ, "sitio")
WA = "https://wa.me/573105996809"
WA_COTIZAR = WA + "?text=Hola%20OMBU%2C%20quiero%20cotizar%20la%20renovaci%C3%B3n%20de%20mi%20espacio."
URL = "https://revupag.github.io/ombu-propuesta/"
LEGAL = "politica-de-datos.html"

ARTICULOS = sorted(ARTICULOS, key=lambda a: a["fecha"], reverse=True)

ICONOS_EXTRA = """    <symbol id="i-chev-d" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></g></symbol>
    <symbol id="i-link" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/></g></symbol>"""


def sprite():
    with open(os.path.join(RAIZ, "herramientas", "iconos.svg.txt"), encoding="utf-8") as f:
        simbolos = f.read()
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">\n  <defs>\n'
            + simbolos + "\n" + ICONOS_EXTRA + "\n  </defs>\n</svg>")


def rutas(nivel):
    """nivel 0 = sitio/index.html, 1 = sitio/blog/*.html, 2 = sitio/legal/*.html"""
    if nivel == 0:
        return {"A": "../assets/", "H": "", "B": "blog/", "P": "../index.html", "L": "legal/" + LEGAL}
    if nivel == 2:
        return {"A": "../../assets/", "H": "../index.html", "B": "../blog/", "P": "../../index.html", "L": LEGAL}
    return {"A": "../../assets/", "H": "../index.html", "B": "", "P": "../../index.html", "L": "../legal/" + LEGAL}


def cabecera(nivel, activo=""):
    r = rutas(nivel)
    H, B = r["H"], r["B"]
    blog_cur = ' aria-current="page"' if activo == "blog" else ""
    solido = "top" if nivel == 0 else "solid"
    return f"""<!-- ============ Encabezado ============ -->
<header class="hdr" id="hdr" data-state="{solido}">
  <div class="hdr__in wrap">
    <a class="hdr__logo" href="{H}#inicio" aria-label="OMBU Renovaciones, ir al inicio">
      <svg class="logo" viewBox="0 0 156 41" aria-hidden="true"><use href="{r['A']}img/marca.svg#ombu-logo"/></svg>
    </a>
    <nav class="hdr__nav" aria-label="Principal">
      <ul>
        <li class="has-drop">
          <button class="hdr__drop-btn" type="button" aria-expanded="false" aria-controls="drop-servicios">Servicios <svg class="chev" aria-hidden="true"><use href="#i-chev-d"/></svg></button>
          <div class="drop" id="drop-servicios" hidden>
            <div class="drop__head">
              <p class="drop__title">Nuestros proyectos</p>
              <a class="link-arrow" href="{H}#servicios">Ver todos <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
            </div>
            <ul class="drop__grid" data-proyectos="drop" role="list"></ul>
          </div>
        </li>
        <li><a href="{H}#por-que">Por qué OMBU</a></li>
        <li><a href="{H}#proceso">Cómo trabajamos</a></li>
        <li><a href="{H}#testimonios">Testimonios</a></li>
        <li><a href="{B}index.html"{blog_cur}>Blog</a></li>
      </ul>
    </nav>
    <a class="btn hdr__cta" href="{H}#contacto">Cotizar</a>
    <button class="hdr__burger" id="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Abrir menú">
      <span></span><span></span>
    </button>
  </div>
</header>

<!-- Menú móvil -->
<div class="menu on-dark" id="menu" hidden>
  <nav class="menu__nav" aria-label="Menú">
    <ul>
      <li>
        <button class="menu__acc" type="button" aria-expanded="false" aria-controls="menu-servicios">Servicios <svg class="chev" aria-hidden="true"><use href="#i-chev-d"/></svg></button>
        <ul class="menu__sub" id="menu-servicios" data-proyectos="menu" role="list" hidden></ul>
      </li>
      <li><a href="{H}#por-que">Por qué OMBU</a></li>
      <li><a href="{H}#proceso">Cómo trabajamos</a></li>
      <li><a href="{H}#testimonios">Testimonios</a></li>
      <li><a href="{B}index.html"{blog_cur}>Blog</a></li>
      <li><a href="{H}#contacto">Contacto</a></li>
    </ul>
  </nav>
  <div class="menu__foot">
    <a class="btn btn--light btn--lg btn--block" href="{WA_COTIZAR}" target="_blank" rel="noopener">
      <svg aria-hidden="true"><use href="#i-wa"/></svg> Escríbenos por WhatsApp
    </a>
    <div class="menu__social">
      <a href="https://www.instagram.com/ombu.renovaciones/" target="_blank" rel="noopener" aria-label="Instagram de OMBU"><svg aria-hidden="true"><use href="#i-ig"/></svg></a>
      <a href="https://www.facebook.com/share/1AA67nPHKe/" target="_blank" rel="noopener" aria-label="Facebook de OMBU"><svg aria-hidden="true"><use href="#i-fb"/></svg></a>
      <a class="menu__back" href="{r['P']}">← Volver a la propuesta</a>
    </div>
  </div>
</div>
"""


def pie(nivel):
    r = rutas(nivel)
    H, B = r["H"], r["B"]
    return f"""<!-- ============ Pie ============ -->
<footer class="ftr on-dark">
  <div class="wrap ftr__grid">
    <div class="ftr__brand">
      <svg class="logo" viewBox="0 0 156 41" role="img" aria-label="OMBU"><use href="{r['A']}img/marca.svg#ombu-logo"/></svg>
      <p>Transforma tu espacio, <em>transforma tu vida.</em></p>
    </div>
    <nav class="ftr__nav" aria-label="Pie de página">
      <ul>
        <li><a href="{H}#servicios">Servicios</a></li>
        <li><a href="{H}#por-que">Por qué OMBU</a></li>
        <li><a href="{H}#proceso">Cómo trabajamos</a></li>
        <li><a href="{B}index.html">Blog</a></li>
        <li><a href="{H}#testimonios">Testimonios</a></li>
        <li><a href="{H}#contacto">Contacto</a></li>
      </ul>
    </nav>
    <div class="ftr__social">
      <p>Síguenos</p>
      <div>
        <a href="https://www.instagram.com/ombu.renovaciones/" target="_blank" rel="noopener" aria-label="Instagram de OMBU"><svg aria-hidden="true"><use href="#i-ig"/></svg></a>
        <a href="https://www.facebook.com/share/1AA67nPHKe/" target="_blank" rel="noopener" aria-label="Facebook de OMBU"><svg aria-hidden="true"><use href="#i-fb"/></svg></a>
        <a href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp de OMBU"><svg aria-hidden="true"><use href="#i-wa"/></svg></a>
      </div>
    </div>
  </div>
  <div class="wrap ftr__bottom">
    <p>© 2026 OMBU Renovaciones · Medellín, Antioquia</p>
    <p class="ftr__legal"><a href="{r['L']}">Política de datos</a><button type="button" data-cookies>Preferencias de cookies</button></p>
    <a href="{r['P']}">← Volver a la propuesta</a>
  </div>
</footer>
"""


def titulo_html(a):
    return f'{a["titulo"]} <em>{a["titulo_em"]}</em>'


def titulo_txt(a):
    return f'{a["titulo"]} {a["titulo_em"]}'


def tarjeta(a, nivel, cabeza="h3"):
    r = rutas(nivel)
    href = f'{r["B"]}{a["slug"]}.html'
    w, h = 768, round(768 * a["portada"][2] / a["portada"][1])
    return f"""<li class="post" data-cat="{a['categoria']}">
  <a class="post__link" href="{href}">
    <div class="post__media"><img src="{r['A']}img/{a['portada_s']}" width="{w}" height="{h}" loading="lazy" decoding="async" alt=""></div>
    <div class="post__body">
      <p class="post__meta"><span class="post__cat">{a['categoria']}</span><span>{a['lectura']} min de lectura</span></p>
      <{cabeza} class="post__title">{titulo_html(a)}</{cabeza}>
      <p class="post__excerpt">{a['resumen']}</p>
      <span class="post__more">Leer artículo <svg aria-hidden="true"><use href="#i-arrow"/></svg></span>
    </div>
  </a>
</li>"""


def avance_blog():
    tarjetas = "\n".join(tarjeta(a, 0) for a in ARTICULOS[:3])
    return f"""<!-- ============ Blog (avance) ============ -->
  <section class="sec blog-teaser" aria-labelledby="bt-title">
    <div class="wrap">
      <div class="sec__head bt__head reveal">
        <div>
          <p class="eyebrow">Blog</p>
          <h2 class="title" id="bt-title">Ideas para <em>tu próximo espacio</em></h2>
        </div>
        <a class="link-arrow" href="blog/index.html">Ver todo el blog <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      </div>
    </div>
    <div class="rail rail--posts" data-rail>
      <ul class="rail__track" role="list" tabindex="0" aria-label="Artículos del blog. Desliza para ver más.">
{tarjetas}
      </ul>
    </div>
  </section>
"""


def head(titulo, descripcion, nivel, og_img, extra_css="", ld=""):
    r = rutas(nivel)
    A = r["A"]
    return f"""<!doctype html>
<html lang="es" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(titulo)}</title>
  <meta name="description" content="{html.escape(descripcion)}">
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#363840">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="es_CO">
  <meta property="og:site_name" content="OMBU Renovaciones">
  <meta property="og:title" content="{html.escape(titulo)}">
  <meta property="og:description" content="{html.escape(descripcion)}">
  <meta property="og:image" content="{URL}assets/img/{og_img}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="{A}img/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="{A}img/favicon-48.png" sizes="48x48" type="image/png">
  <link rel="apple-touch-icon" href="{A}img/apple-touch-icon.png">
  <link rel="preload" href="{A}fonts/poppins-900.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{A}fonts/poppins-300.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{A}css/brand.css">
  <link rel="stylesheet" href="{A}css/sitio.css">
  <link rel="stylesheet" href="{A}css/blog.css">{extra_css}
{ld}  <script>document.documentElement.classList.replace('no-js', 'js');</script>
</head>
"""


def scripts(nivel, extra=""):
    A = rutas(nivel)["A"]
    return f"""<script src="{A}js/proyectos.js"></script>
<script src="{A}js/comun.js"></script>
<script src="{A}js/blog.js"></script>{extra}
</body>
</html>
"""


def cuerpo_comun(nivel, activo="blog"):
    return sprite() + '\n\n<a class="skip" href="#contenido">Saltar al contenido</a>\n\n' + cabecera(nivel, activo)


def fab():
    return f"""<a class="fab" id="fab" href="{WA_COTIZAR}" target="_blank" rel="noopener" aria-label="Escríbenos por WhatsApp">
  <svg aria-hidden="true"><use href="#i-wa"/></svg>
</a>
"""


def pagina_indice():
    destacado = ARTICULOS[0]
    resto = "\n".join(tarjeta(a, 1) for a in ARTICULOS[1:])
    cats = sorted({a["categoria"] for a in ARTICULOS})
    chips = '\n'.join(f'          <button class="filter" type="button" aria-pressed="false" data-filter="{c}">{c}</button>' for c in cats)
    d = destacado
    return (head("Blog · OMBU Renovaciones", "Guías e ideas para renovar tu apartamento, casa u oficina en Medellín, del equipo de OMBU.", 1, "og-sitio.jpg")
            + '<body data-page="blog" data-root="../../" data-home="../index.html">\n' + cuerpo_comun(1) + f"""
<main id="contenido">
  <section class="bhero" aria-labelledby="bhero-title">
    <div class="wrap">
      <nav class="crumbs" aria-label="Ruta"><a href="../index.html">Inicio</a><span aria-hidden="true">/</span><span aria-current="page">Blog</span></nav>
      <h1 class="display bhero__title" id="bhero-title">Ideas para transformar <em>tu espacio</em></h1>
      <p class="lead">Guías prácticas, ideas de diseño y lo que aprendemos en cada obra. Para que tu renovación empiece con las decisiones correctas.</p>
    </div>
  </section>

  <section class="wrap blist" aria-label="Artículos">
    <article class="feature reveal" data-cat="{d['categoria']}">
      <a class="feature__link" href="{d['slug']}.html">
        <div class="feature__media"><img src="../../assets/img/{d['portada'][0]}" width="{d['portada'][1]}" height="{d['portada'][2]}" alt="{d['portada_alt']}" fetchpriority="high"></div>
        <div class="feature__body">
          <p class="post__meta"><span class="post__cat">{d['categoria']}</span><span>{d['fecha_txt']}</span><span>{d['lectura']} min</span></p>
          <h2 class="feature__title">{titulo_html(d)}</h2>
          <p class="post__excerpt">{d['resumen']}</p>
          <span class="btn">Leer artículo <svg aria-hidden="true"><use href="#i-arrow"/></svg></span>
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

{banda()}
</main>

""" + pie(1) + fab() + scripts(1))


def banda():
    return """  <section class="band on-dark" aria-labelledby="band-title">
    <picture class="band__media" aria-hidden="true">
      <img src="../../assets/img/proyectos/palo-alto/d01-s.webp" width="768" height="512" loading="lazy" decoding="async" alt="">
    </picture>
    <div class="wrap band__in reveal">
      <h2 class="band__title display" id="band-title">¿Listo para dar el primer paso <em>hacia tu nuevo hogar?</em></h2>
      <p class="lead">Comienza tu renovación con expertos.</p>
      <a class="btn btn--light btn--lg" href="../index.html#contacto">Quiero cotizar <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
    </div>
  </section>"""


def pagina_articulo(a):
    otros = [x for x in ARTICULOS if x["slug"] != a["slug"]]
    rel = "\n".join(tarjeta(x, 1) for x in otros)
    cuerpo = a["cuerpo"].replace("{A}", "../../assets/")
    ld = f"""  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BlogPosting","headline":{jsonstr(titulo_txt(a))},"description":{jsonstr(a['resumen'])},
   "datePublished":"{a['fecha']}","image":"{URL}assets/img/{a['portada'][0]}","author":{{"@type":"Organization","name":"OMBU Renovaciones"}},
   "publisher":{{"@type":"Organization","name":"OMBU Renovaciones","logo":{{"@type":"ImageObject","url":"{URL}assets/img/icon-512.png"}}}}}}
  </script>
"""
    share_txt = f'{titulo_txt(a)} · OMBU Renovaciones'
    return (head(f'{titulo_txt(a)} · Blog OMBU', a["resumen"], 1, "og-sitio.jpg", ld=ld)
            + '<body data-page="articulo" data-root="../../" data-home="../index.html">\n' + cuerpo_comun(1) + f"""
<main id="contenido">
  <article class="art">
    <header class="art__head wrap">
      <nav class="crumbs" aria-label="Ruta"><a href="../index.html">Inicio</a><span aria-hidden="true">/</span><a href="index.html">Blog</a><span aria-hidden="true">/</span><span aria-current="page">{a['categoria']}</span></nav>
      <p class="post__meta"><span class="post__cat">{a['categoria']}</span><span><time datetime="{a['fecha']}">{a['fecha_txt']}</time></span><span>{a['lectura']} min de lectura</span></p>
      <h1 class="display art__title">{titulo_html(a)}</h1>
      <p class="lead art__lead">{a['resumen']}</p>
      <p class="art__by"><span class="art__avatar" aria-hidden="true"><svg viewBox="0 0 2250 2250"><use href="../../assets/img/marca.svg#ombu-mark"/></svg></span><span><strong>Equipo OMBU</strong>Arquitectos y especialistas en renovación</span></p>
    </header>
    <figure class="art__cover wrap">
      <img src="../../assets/img/{a['portada'][0]}" width="{a['portada'][1]}" height="{a['portada'][2]}" alt="{a['portada_alt']}" fetchpriority="high">
      <figcaption>{a['pie_portada']}</figcaption>
    </figure>
    <div class="art__layout wrap">
      <div class="prose">
{cuerpo}
      </div>
      <aside class="art__side">
        <div class="share" aria-label="Compartir">
          <p>Compartir</p>
          <a class="icon-btn" href="https://wa.me/?text={urlq(share_txt)}%20" data-share-wa target="_blank" rel="noopener" aria-label="Compartir por WhatsApp"><svg aria-hidden="true"><use href="#i-wa"/></svg></a>
          <button class="icon-btn" type="button" data-copy aria-label="Copiar enlace"><svg aria-hidden="true"><use href="#i-link"/></svg></button>
          <span class="share__ok" role="status"></span>
        </div>
      </aside>
    </div>
    <section class="wrap art__cta reveal" aria-labelledby="cta-title">
      <div class="cta-box on-dark">
        <svg class="cta-box__mark" viewBox="0 0 2250 2250" aria-hidden="true"><use href="../../assets/img/marca.svg#ombu-mark"/></svg>
        <h2 class="cta-box__title" id="cta-title">¿Quieres transformar <em>tu espacio?</em></h2>
        <p>Cuéntanos qué tienes en mente y te asesoramos de manera personalizada.</p>
        <div class="cta-box__btns">
          <a class="btn btn--light btn--lg" href="../index.html#contacto">Cotizar mi proyecto <svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
          <a class="btn btn--ghost btn--lg" href="{WA_COTIZAR}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-wa"/></svg> WhatsApp</a>
        </div>
      </div>
    </section>
  </article>

  <section class="sec related" aria-labelledby="rel-title">
    <div class="wrap"><div class="sec__head"><p class="eyebrow">Sigue leyendo</p><h2 class="title" id="rel-title">Más ideas <em>del blog</em></h2></div></div>
    <div class="rail rail--posts" data-rail>
      <ul class="rail__track" role="list" tabindex="0" aria-label="Otros artículos. Desliza para ver más.">
{rel}
      </ul>
    </div>
  </section>
</main>

""" + pie(1) + fab() + scripts(1))


PEND = '<mark class="pend">por confirmar</mark>'


def pagina_politica():
    return (head("Política de tratamiento de datos · OMBU Renovaciones", "Cómo OMBU Renovaciones recolecta, usa y protege tus datos personales, y cómo ejercer tus derechos.", 2, "og-sitio.jpg")
            + '<body data-page="legal" data-root="../../" data-home="../index.html">\n' + cuerpo_comun(2, "") + f"""
<main id="contenido">
  <article class="art legal">
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
          <li><strong>Datos de contacto:</strong> nombre y número de celular que escribes en el formulario o nos envías por WhatsApp.</li>
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
        <p>Al enviar el formulario o escribirnos por WhatsApp nos autorizas a tratar tus datos para las finalidades anteriores. Guardamos prueba de esa autorización (el mensaje recibido) mientras dure la relación contigo.</p>

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
</main>

""" + pie(2) + fab() + scripts(2))


def jsonstr(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def urlq(s):
    from urllib.parse import quote
    return quote(s)


def reemplazar(texto, nombre, contenido):
    patron = re.compile(r"(<!-- @%s -->\n).*?(<!-- /@%s -->)" % (nombre, nombre), re.S)
    nuevo, n = patron.subn(lambda m: m.group(1) + contenido.rstrip() + "\n" + m.group(2), texto)
    assert n == 1, nombre
    return nuevo


def main():
    ruta = os.path.join(SITIO, "index.html")
    with open(ruta, encoding="utf-8") as f:
        s = f.read()
    s = reemplazar(s, "sprite", sprite())
    s = reemplazar(s, "cabecera", cabecera(0))
    s = reemplazar(s, "pie", pie(0))
    s = reemplazar(s, "blog-teaser", avance_blog())
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(s)

    os.makedirs(os.path.join(SITIO, "blog"), exist_ok=True)
    with open(os.path.join(SITIO, "blog", "index.html"), "w", encoding="utf-8") as f:
        f.write(pagina_indice())
    for a in ARTICULOS:
        with open(os.path.join(SITIO, "blog", a["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(pagina_articulo(a))
    os.makedirs(os.path.join(SITIO, "legal"), exist_ok=True)
    with open(os.path.join(SITIO, "legal", LEGAL), "w", encoding="utf-8") as f:
        f.write(pagina_politica())
    print("Generado: sitio/index.html,", len(ARTICULOS) + 1, "páginas del blog y la política de datos")


if __name__ == "__main__":
    main()
