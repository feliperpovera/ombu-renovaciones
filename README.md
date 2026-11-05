# OMBU Renovaciones · sitio web y panel de edición

Sitio de **OMBU Renovaciones** (Medellín) y un panel para editar textos, fotos, servicios, proyectos y blog sin tocar código. Misma estructura que el proyecto Wanna Go.

| | Dirección |
|---|---|
| Sitio | https://feliperpovera.github.io/ombu-renovaciones/ |
| Panel de edición | https://feliperpovera.github.io/ombu-renovaciones/admin/ |
| Panel en modo demo (no guarda) | https://feliperpovera.github.io/ombu-renovaciones/admin/?demo |

## Cómo funciona

1. **El panel** (`/admin`) guarda en **Supabase** lo que se edita.
2. **«Publicar cambios»** llama a la función `publicar`, que le pide a GitHub construir el sitio.
3. **GitHub Actions** baja el contenido de Supabase a `contenido/` (queda copia en el repositorio), optimiza las fotos y arma las páginas en `dist/`.
4. La acción publica `dist/` en GitHub Pages. Tarda 2 a 3 minutos. El sitio es estático: carga rápido y Google lo lee completo.

## Estructura

```
contenido/      Lo que edita el panel (copia de Supabase)
  paginas/      Un archivo por página, más general.json (contacto, datos legales, pie, testimonios, preguntas…)
  servicios/    Un archivo por servicio
  proyectos/    Un archivo por proyecto
  blog/         Un archivo por entrada
fotos/          Fotos originales (las optimiza la construcción)
assets/         CSS, JS, fuentes y marca
panel/          Panel de edición, se publica en /admin (esquema.js define los campos de cada página)
herramientas/   generar.py (arma dist/), fotos.py (WebP 800 y 1600 px), supabase/bajar.mjs y semilla.mjs
supabase/       migrations/, functions/publicar/, seed.sql e instalar.sql (esquema + contenido en un solo archivo)
dist/           El sitio construido (no se sube; lo arma GitHub)
```

No editar HTML a mano: todo sale de `contenido/` y de las plantillas de `herramientas/generar.py`.

## Trabajar en local

Requiere Python 3 con Pillow (`pip install pillow`) y Node 20 o más.

```bash
npm run construir
```

```bash
npm run ver
```

Luego abre http://localhost:8765 para el sitio y http://localhost:8765/admin/?demo para el panel.

## Qué se edita en el panel

| Sección | Qué permite |
|---|---|
| **Páginas** | Datos generales (WhatsApp, redes, NIT, dirección, correo, pie, banda final, atributos, pasos, testimonios, preguntas), Inicio, Nosotros, Servicios, Proyectos, Contacto, Blog y los 4 documentos legales. |
| **Servicios** | Editar, crear (con su propia página) y borrar. Incluye el catálogo de mobiliario. |
| **Proyectos** | Editar, crear, ordenar y borrar. Fotos de antes y después, ficha, «Destacado» para que salga en el inicio. Sin fotos sale «Fotos pendientes». |
| **Blog** | Escribir entradas con foto, como borrador o publicadas. Formato sencillo: `## subtítulo`, `**negrita**`, `*cursiva*`, `- lista`, `> cita`, `[texto](enlace)`, `![descripción](archivo.webp "pie")`. |
| **Solicitudes** | Lo que llega por el formulario de contacto (además de abrir WhatsApp). |
| **Publicaciones** | Historial del botón «Publicar cambios». |

**Fijo a propósito** (para no romper el diseño): menú, colores y orden de las secciones. Para volver editable algo nuevo: agregar el campo en `panel/esquema.js`, en `contenido/` y en la plantilla de `herramientas/generar.py`.

## Seguridad

- **Acceso al panel:** correo y contraseña. Cada editor crea su contraseña desde el correo de invitación (o con «Olvidé mi contraseña»); nadie más la conoce. Solo entran los correos de la tabla `editores`.
- **Permisos en la base (RLS):** el público solo lee lo publicado y puede enviar el formulario. Solo los editores escriben, suben fotos y leen solicitudes.
- **Claves:** en el repositorio solo va la clave pública de Supabase (`panel/config.js`). La clave `service_role` y el token de GitHub nunca se suben.

## Conectar Supabase

1. Crear el proyecto en Supabase (región São Paulo).
2. SQL Editor: pegar y ejecutar `supabase/instalar.sql` (tablas, permisos, fotos, contenido y el editor ombumercadeo@gmail.com).
3. Authentication → URL Configuration: Site URL y Redirect URL `https://feliperpovera.github.io/ombu-renovaciones/admin/`.
4. Authentication → Users → Invite user: `ombumercadeo@gmail.com`. Ese correo crea la contraseña.
5. Edge Functions: crear la función `publicar` con `supabase/functions/publicar/index.ts` y los secretos `GITHUB_REPO` = `feliperpovera/ombu-renovaciones` y `GITHUB_TOKEN` (token fine-grained solo de este repositorio, permiso *Contents: Read and write*).
6. Llenar `panel/config.js` con la URL del proyecto y la clave pública (publishable).
7. GitHub → Settings → Secrets and variables → Actions → **Variables**: `SUPABASE_URL` y `SUPABASE_ANON_KEY` (la misma clave pública).

## Antes de salir en vivo

- Quitar `noindex` en `head()` de `herramientas/generar.py` y cambiar `URL` cuando esté en su dominio.
- Completar desde el panel: NIT, dirección y correo (Datos generales), y las fotos pendientes.
