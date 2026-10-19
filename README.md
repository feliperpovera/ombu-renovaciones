# OMBU Renovaciones — Propuesta de sitio web

Propuesta comercial y demostración navegable del nuevo sitio web de
**OMBU Renovaciones** (Medellín, Colombia).

### ▶ Ver en vivo

**https://revupag.github.io/ombu-propuesta/**

Ese es el enlace para enviarle al cliente. Abre en la propuesta; el botón
«Sí, quiero ver mi página» lleva al sitio terminado, y desde el sitio (menú y
pie de página) hay un enlace de vuelta. Pensado para abrirse desde el celular.

---

## Qué contiene

| Ruta | Qué es |
|---|---|
| `index.html` | La **propuesta**: diagnóstico del sitio actual, lo que vamos a construir, comparativa antes/después, proceso y entregables. Termina en el CTA que lleva al sitio. |
| `sitio/` | El **sitio terminado** según «Estructura y contenidos»: Inicio (resumen de todo), `nosotros.html` (incluye cómo trabajamos), `servicios/` (índice + Diseño, Construcción, Mobiliario, Interventoría), `proyectos.html` (galerías y antes/después con ficha), `contacto.html` (formulario + preguntas frecuentes) y `legal/politica-de-datos.html`. |
| `sitio/blog/` | **Blog**: índice con artículo destacado y filtro por temas, y cuatro artículos. |
| `herramientas/generar.py` | Genera **todas** las páginas de `sitio/` (textos, menú, pie y secciones repetidas). Los artículos están en `herramientas/articulos.py`. |
| `assets/css/brand.css` | Sistema de marca: color, tipografía, escala y componentes base. |
| `assets/css/propuesta.css` · `sitio.css` | Estilos de cada página. |
| `assets/js/proyectos.js` | Los 13 proyectos con sus fotos clasificadas en «antes» y «después». |
| `assets/js/comun.js` | Cabecera, desplegable de Servicios, menú móvil, carriles y WhatsApp flotante (todas las páginas). |
| `assets/js/inicio.js` · `blog.js` | Tarjetas con comparador, ficha, visor y formulario (Inicio, Proyectos, Contacto); filtro y compartir del blog. Sin librerías externas. |
| `assets/img/marca.svg` | Logo y símbolo de OMBU en vectorial. |
| `assets/img/proyectos/` | 188 fotos de obra en WebP, en dos tamaños. |

---

## Branding

Todo se extrajo de `omburenovaciones.com`; nada se inventó.

**Color** — tomado del kit global de Elementor del sitio actual (`post-6.css`)
y del CSS de cada página:

| Token | Valor | Origen | Uso |
|---|---|---|---|
| `--ombu-carbon` | `#363840` | Global «14d4955» y color del logo | Titulares, fondos oscuros |
| `--ombu-lavanda` | `#D7DAEF` | Global «0cf1c55» | Texto sobre carbón, círculos de acento |
| `--ombu-pizarra` | `#6D7180` | Botones del sitio actual | Botón principal, texto secundario |
| `--ombu-lila` | `#C1C6E5` | Acento del inicio | Reserva |
| `--ombu-niebla` | `#F2F2F2` | Superficie clara del inicio | Fondos de sección |

**Tipografía** — **Poppins**, la misma que el sitio actual aloja en su servidor.
Se conserva la firma visual del sitio: titular en Poppins 900 y segunda línea en
Poppins 300 cursiva. Las fuentes van alojadas en el propio sitio (WOFF2,
≈ 48 KB en total), sin llamadas a Google.

**Logo** — el sitio solo publica el logo completo en 156 × 40 px, que se ve
borroso en un celular. Se reconstruyó en vectorial **sin redibujarlo a ojo**:

- El símbolo se midió sobre el archivo original de 2250 px del favicon
  (`Ombu.webp`); el vector coincide con él en un **99,5 %** de los píxeles.
- Las letras «MBU» son **Poppins Medium**: se compararon 63 variantes de 21 familias tipográficas
  contra el logo original y Poppins Medium coincide en un **97 %** (el resto
  es la compresión del archivo original).
- Color exacto del logo: `#363840`.

Los archivos originales del cliente están en `assets/img/logo-original-*.webp`
para comparar.

### Una nota honesta sobre accesibilidad

El pizarra `#6D7180` cumple AA sobre blanco (4,86:1), pero sobre el fondo
niebla `#F2F2F2` da 4,34:1 y **no** alcanza para texto pequeño. Solo en esas
superficies el texto secundario usa `#5E6270` (5,4:1), el mismo tono
oscurecido. El botón y todo lo demás conservan el color exacto.

---

## Diagnóstico del sitio actual

Verificado el 30 de septiembre de 2026 en un celular de 375 px:

- Primera pantalla sin botón de acción: el primero está a 1.461 px de scroll y
  «Escríbenos» a 4.129 px.
- La página de Contacto no tiene formulario, teléfono ni correo.
- Cero etiquetas Open Graph y ninguna meta descripción; título de portada «Ombu».
- Proyectos sin ficha; **Kuna 1002 y Kuna 802 muestran las mismas 21 fotos de
  «antes»** (obra gris del mismo edificio). En la demo cada uno usa una selección
  distinta de esas fotos; hay que confirmar cuáles son de cada apartamento.
- Portada: 80 archivos, 2,5 MB, 32 hojas de estilo y 27 scripts, WordPress
  6.8 + Elementor + 7 plugins, sin carga diferida de imágenes.
- «Inspírate con nuestro resultados», buscador «Search …», «Siguenos», portada
  sin H1, © 2025.

El sitio nuevo carga **25 archivos y 0,6 MB** en la misma prueba.

---

## Cómo editar textos, páginas o el blog

Todo el HTML de `sitio/` sale de `herramientas/generar.py` (no se edita a mano).
Cambia ahí los textos o, para un artículo, `herramientas/articulos.py`, y ejecuta:

```bash
python3 herramientas/generar.py
```

---

## Cómo verlo en local

No requiere compilación ni dependencias:

```bash
python3 -m http.server 4174
```

Y abrir `http://localhost:4174`.

---

## Publicación

Publicado con **GitHub Pages** desde la rama `main`, carpeta raíz. El archivo
`.nojekyll` hace que GitHub sirva la carpeta tal cual.

Para actualizar el sitio en vivo basta con subir los cambios (tarda un par de
minutos):

```bash
git add -A && git commit -m "..." && git push
```

Ambas páginas llevan `<meta name="robots" content="noindex, nofollow">`, así que
no aparecen en Google aunque el repositorio sea público. Hay que quitarlo el día
que el sitio se publique bajo `omburenovaciones.com`.

---

## Decisiones técnicas

- **HTML, CSS y JavaScript planos.** Sin framework, sin build, sin dependencias.
- **Mobile-first.** Diseñado a 375 px y expandido en 600, 960 y 1200 px.
  Tipografía fluida con `clamp()`, objetivos táctiles de 48 px, campos de
  16 px (sin zoom automático en iOS) y cero desplazamiento horizontal.
- **Comparador antes/después.** Se arrastra en toda la foto con Pointer Events
  (en iOS un `input range` solo responde tocando el pulgar) y sigue siendo un
  `range` accesible con teclado y lector de pantalla. Al entrar en pantalla hace
  una pequeña demostración para que se entienda que se desliza.
- **Servicios.** En escritorio, «Servicios» abre un desplegable con los 13
  proyectos y su miniatura; en el celular es un acordeón dentro del menú. Cada
  proyecto abre su ficha directamente.
- **Comparador en cada tarjeta.** Cada proyecto del carrusel muestra una foto de
  antes y una de después **del mismo espacio**, elegidas a mano entre las 471 fotos
  publicadas. Con el dedo se arrastra desde el tirador central (el resto de la foto
  sigue deslizando el carrusel y un toque abre el proyecto); con el mouse, desde
  cualquier punto. También funciona con el teclado.
- **Proyectos.** Carrusel con `scroll-snap` nativo y vista en cuadrícula. Cada
  proyecto abre una ficha (`<dialog>`) con pestañas «Después» / «Antes»,
  galería y visor a pantalla completa con gesto de deslizar. Cada ficha tiene
  URL propia (`#proyecto/kuna-1002`), se puede compartir y el botón «atrás» del
  celular la cierra.
- **WhatsApp con contexto.** «Quiero un proyecto así» abre WhatsApp con el
  nombre del proyecto escrito, y el formulario de contacto valida y arma el
  mensaje completo (nombre, tipo de espacio, idea y celular). Funciona hoy, sin
  servidor.
- **SEO.** Título y descripción por página, Open Graph con imagen propia,
  datos estructurados `GeneralContractor` de Schema.org.
- **Marca en todo.** El botón flotante de WhatsApp pasó del verde genérico al
  carbón de OMBU con anillo lavanda; no queda ningún color fuera de la paleta,
  salvo el rojo de los errores del formulario.
- **Accesibilidad.** Un solo `h1` por página, jerarquía sin saltos, formulario
  etiquetado con errores anunciados, foco visible, navegación por teclado en
  carruseles, pestañas y visor, `prefers-reduced-motion` respetado y **cero
  fallos de contraste** en la auditoría automática de la propuesta, el sitio y el blog.

---

## Qué falta definir con el cliente

- **Ficha de cada proyecto.** El sitio actual no tiene textos por proyecto. La
  demo muestra una nota donde irán tipo de espacio, metros, alcance y tiempos.
- **Fotos de «antes» de Kuna 1002 y Kuna 802.** Hoy son las mismas en ambos.
- **Blog.** Los cuatro artículos son una propuesta de redacción con consejos
  generales y fotos reales de sus obras; deben ser revisados y aprobados por OMBU.
- **Textos de «Cómo trabajamos».** Los cuatro pasos se redactaron a partir de
  lo que el sitio actual dice (asesoría personalizada, arquitectos, pólizas,
  «cumplir lo acordado»). Deben ser aprobados por OMBU.
- **Testimonios.** Son los cuatro del sitio actual, textuales. Con foto y
  enlace a Google Reviews ganan credibilidad.
- **Correo y teléfono fijo**, si los hay. Hoy el único canal publicado es el
  WhatsApp +57 310 599 6809.
- **Formulario por correo.** Hoy envía a WhatsApp; falta conectar el aviso por
  correo.
- **Propuesta económica.** Se entrega en documento aparte.

---

Preparado por **RevUp Agency Group** · 2026
