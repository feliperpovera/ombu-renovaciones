// Panel OMBU · edita en Supabase el contenido del sitio y pide publicarlo.
// Guardar cambia la base de datos; «Publicar cambios» regenera el sitio en GitHub (2 a 3 minutos).
// Con ?demo se prueba sin Supabase: lee demo.json (el contenido actual) y no guarda nada.
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/+esm';
import { PAGINAS } from './esquema.js?v=1';

const CFG = window.OMBU_SUPABASE || {};
const DEMO = new URLSearchParams(location.search).has('demo');
const SITIO = new URL('../', location.href).href;
// Si se llega desde el correo de invitación o de «olvidé mi contraseña», hay que crear una contraseña nueva
const CREAR_CLAVE = /type=(invite|recovery)/.test(location.hash);
const sb = CFG.url && CFG.clave && !DEMO ? createClient(CFG.url, CFG.clave) : null;
const hoy = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Bogota' });

// ---------- utilidades ----------

const h = (tag, attrs = {}, ...hijos) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (k === 'class') el.className = v;
    else if (k in el && !k.includes('-')) el[k] = v;
    else el.setAttribute(k, v === true ? '' : v);
  }
  el.append(...hijos.flat(Infinity).filter(x => x != null && x !== false));
  return el;
};
const app = document.getElementById('app');
const toast = (texto, error) => {
  const t = document.getElementById('toast');
  t.textContent = texto;
  t.className = error ? 'on error' : 'on';
  clearTimeout(toast.reloj);
  toast.reloj = setTimeout(() => (t.className = ''), 5000);
};
const listo = m => toast(DEMO ? `${m} (modo demo: solo en esta pestaña)` : m);
const fallo = e => toast(e?.message || String(e), true);
const copia = o => structuredClone(o);
const raiz = f => (f || '').replace(/\.[a-z]+$/i, '');
const demoFotos = {};
const fotoURL = f => demoFotos[f] || `${SITIO}fotos/${raiz(f)}-800.webp`;
const fotoRespaldo = f => (CFG.url ? `${CFG.url}/storage/v1/object/public/fotos/${encodeURIComponent(f)}` : '');
const limpio = nombre => nombre.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  .replace(/[^a-z0-9.]+/g, '-').replace(/^-+|-+$/g, '');
const boton = (texto, fn, { off, cls = 'mini', titulo } = {}) => h('button', { type: 'button', class: cls, onclick: fn, disabled: off, title: titulo, 'aria-label': titulo }, texto);
const miniatura = f => {
  const img = h('img', { alt: '', loading: 'lazy' });
  if (f) { img.onerror = () => { img.onerror = null; img.src = fotoRespaldo(f); }; img.src = fotoURL(f); }
  return img;
};

// ---------- datos: Supabase o demo ----------

const api = sb ? {
  async listar(t, orden = 'orden', desc = false) {
    const { data, error } = await sb.from(t).select('*').order(orden, { ascending: !desc });
    if (error) throw error;
    return data;
  },
  async guardar(t, filas, nuevo) {
    const { error } = nuevo ? await sb.from(t).insert(filas) : await sb.from(t).upsert(filas);
    if (error) throw new Error(error.code === '23505' ? 'Ya existe un registro con esa dirección (url).' : error.message);
  },
  async borrar(t, col, val) {
    const { error } = await sb.from(t).delete().eq(col, val);
    if (error) throw error;
  },
  async subir(archivo) {
    const base = limpio(archivo.name);
    const subir = n => sb.storage.from('fotos').upload(n, archivo, { contentType: archivo.type });
    let nombre = base, { error } = await subir(nombre);
    if (error && /exist|duplicate/i.test(error.message)) {
      nombre = base.replace(/(\.[a-z]+)$/i, `-${Date.now().toString(36)}$1`);
      ({ error } = await subir(nombre));
    }
    if (error) throw error;
    return nombre;
  },
  async publicar() {
    const { error } = await sb.functions.invoke('publicar');
    if (error) throw new Error('No se pudo publicar: ' + error.message);
  },
} : demoApi();

function demoApi() {
  let db;
  const cargar = async () => {
    if (db) return db;
    const r = await fetch('demo.json');
    if (!r.ok) throw new Error('No se encontró demo.json: corre npm run construir');
    const { paginas, servicios, proyectos, blog } = await r.json();
    db = {
      paginas: PAGINAS.map(p => ({ id: p.id, contenido: paginas[p.id] })),
      servicios, proyectos, blog, solicitudes: [], publicaciones: [],
    };
    return db;
  };
  const clave = t => (t === 'paginas' ? 'id' : 'url');
  return {
    async listar(t, orden = 'orden', desc = false) {
      const d = await cargar();
      return copia(d[t]).sort((a, b) => ((a[orden] > b[orden]) - (a[orden] < b[orden])) * (desc ? -1 : 1));
    },
    async guardar(t, filas, nuevo) {
      const d = await cargar(), k = clave(t);
      for (const f of [].concat(filas)) {
        f[k] ??= crypto.randomUUID();
        const i = d[t].findIndex(x => x[k] === f[k]);
        if (i >= 0 && nuevo) throw new Error('Ya existe un registro con esa dirección (url).');
        if (i < 0) d[t].push(copia(f)); else d[t][i] = { ...d[t][i], ...copia(f) };
      }
    },
    async borrar(t, col, val) {
      const d = await cargar();
      d[t] = d[t].filter(x => x[col] !== val);
    },
    async subir(archivo) {
      const n = limpio(archivo.name);
      demoFotos[n] = URL.createObjectURL(archivo);
      return n;
    },
    async publicar() {},
  };
}

// ---------- campos de formulario ----------

const FORMATO = 'Formato: deja una línea en blanco entre párrafos. ## Subtítulo · ### Subtítulo menor · **negrita** · *cursiva* · - lista · > cita · [texto del enlace](https://…) · ![descripción](archivo.webp "pie de foto")';
const ICONOS = [['i-design', 'Diseño'], ['i-build', 'Construcción'], ['i-sofa', 'Mobiliario'], ['i-clipboard', 'Interventoría'], ['i-plan', 'Plano'], ['i-key', 'Llave'], ['i-shield', 'Escudo'], ['i-people', 'Personas']];
const URL_CAMPO = (ruta, ej) => ({ tipo: 'texto', name: 'url', label: 'Dirección (url)', fija: true, patron: '[a-z0-9-]+',
  ayuda: `La página queda en ${ruta}. Solo minúsculas, números y guiones${ej ? ', ej.: ' + ej : ''}. No se puede cambiar después de crear.` });
const T = (label, name, o = {}) => ({ tipo: 'texto', label, name, ...o });
const L = (label, name, o = {}) => ({ tipo: 'largo', label, name, ...o });
const CAMPOS = {
  servicios: [
    URL_CAMPO('servicios/<url>.html'),
    { tipo: 'numero', name: 'orden', label: 'Orden' },
    { tipo: 'bool', name: 'publicado', label: 'Publicado en el sitio' },
    T('Nombre', 'nombre'),
    { tipo: 'opciones', name: 'icono', label: 'Icono', opciones: ICONOS },
    L('Resumen para tarjetas', 'resumen'),
    T('Titular (parte en negrita)', 'titulo'), T('Titular (parte en cursiva)', 'titulo_em'),
    L('Texto de apoyo', 'texto'),
    { tipo: 'foto', name: 'foto', label: 'Foto principal' }, T('Descripción de la foto', 'alt'),
    T('Título de la lista', 'lista_titulo', { ayuda: 'Ej.: ¿Qué incluye?' }),
    { tipo: 'lista', name: 'lista', label: 'Lista', nuevo: '', item: T('', '') },
    T('Texto del botón', 'cta'),
    { tipo: 'servicios', name: 'ocultar', label: 'No mostrar en «Otros servicios»', ayuda: 'Marca los servicios que no deben salir como complemento en esta página.' },
    T('Catálogo: titular (negrita)', 'catalogo_titulo'), T('Catálogo: titular (cursiva)', 'catalogo_titulo_em'), L('Catálogo: texto', 'catalogo_texto'),
    { tipo: 'lista', name: 'piezas', label: 'Catálogo: piezas', nuevo: { foto: '', nombre: '' }, ayuda: 'Si no hay piezas, la sección de catálogo no sale.',
      campos: [{ tipo: 'foto', name: 'foto', label: 'Foto' }, T('Nombre', 'nombre')] },
  ],
  proyectos: [
    URL_CAMPO('proyectos.html#proyecto/<url>'),
    { tipo: 'numero', name: 'orden', label: 'Orden' },
    { tipo: 'bool', name: 'publicado', label: 'Publicado en el sitio' },
    { tipo: 'bool', name: 'destacado', label: 'Destacado (sale en el inicio)' },
    T('Nombre', 'nombre'),
    T('Tipo de espacio', 'tipo', { ayuda: 'Ej.: Apartamento' }),
    T('Servicios realizados', 'servicios', { ayuda: 'Ej.: Diseño y construcción' }),
    L('Breve descripción', 'descripcion'),
    { tipo: 'foto', name: 'foto_antes', label: 'Comparador: foto de antes' },
    { tipo: 'foto', name: 'foto_despues', label: 'Comparador: foto de después' },
    { tipo: 'lista', name: 'despues', label: 'Fotos del resultado (después)', nuevo: '', item: { tipo: 'foto', name: '', label: '' } },
    { tipo: 'lista', name: 'antes', label: 'Fotos del estado inicial (antes)', nuevo: '', item: { tipo: 'foto', name: '', label: '' } },
  ],
  blog: [
    URL_CAMPO('blog/<url>.html', 'que-hacer-en-una-cocina-pequena'),
    { tipo: 'bool', name: 'publicado', label: 'Publicada en el sitio (si está apagado, queda como borrador)' },
    { tipo: 'fecha', name: 'fecha', label: 'Fecha' },
    T('Autor', 'autor'), T('Categoría', 'categoria', { ayuda: 'Ej.: Diseño e interiorismo, Consejos para renovar, Materiales y acabados, Procesos de construcción, Inspiración y tendencias' }),
    { tipo: 'numero', name: 'lectura', label: 'Minutos de lectura' },
    T('Título (parte en negrita)', 'titulo', { max: 70 }), T('Título (parte en cursiva)', 'titulo_em'),
    { tipo: 'foto', name: 'foto', label: 'Foto principal' },
    T('Descripción de la foto', 'alt'), T('Pie de foto', 'pie_foto'),
    L('Resumen (sale en la lista del blog y en Google)', 'resumen', { max: 160 }),
    L('Texto de la entrada', 'cuerpo', { filas: 18, ayuda: FORMATO }),
  ],
};

const contador = (el, max) => {
  const c = h('span', { class: 'contador' });
  const act = () => { c.textContent = `${el.value.length} / ${max}`; c.classList.toggle('pasado', el.value.length > max); };
  el.addEventListener('input', act); act();
  return c;
};

function campo(def, valor, ctx = {}) {
  const id = 'c' + Math.random().toString(36).slice(2, 9);
  const ayuda = def.ayuda && h('small', { class: 'ayuda' }, def.ayuda);
  const etiqueta = h('label', { class: 'lbl', for: id }, def.label);
  switch (def.tipo) {
    case 'texto': case 'numero': case 'fecha': {
      const i = h('input', { id, type: { numero: 'number', fecha: 'date' }[def.tipo] || 'text', value: valor ?? '', pattern: def.patron, readOnly: def.fija && ctx.existente });
      const leer = () => def.tipo === 'numero' ? Number(i.value || 0) : def.tipo === 'fecha' ? (i.value || null) : i.value.trim();
      return { el: h('div', { class: 'campo' }, etiqueta, i, ayuda), leer };
    }
    case 'largo': {
      const i = h('textarea', { id, rows: def.filas || 3, value: valor ?? '' });
      return { el: h('div', { class: 'campo' }, etiqueta, i, def.max && contador(i, def.max), ayuda), leer: () => i.value.trim() };
    }
    case 'bool': {
      const i = h('input', { id, type: 'checkbox', checked: !!valor });
      return { el: h('label', { class: 'campo interruptor', for: id }, i, h('span', {}, def.label)), leer: () => i.checked };
    }
    case 'opciones': {
      const i = h('select', { id }, def.opciones.map(([v, t]) => h('option', { value: v, selected: v === valor }, t)));
      return { el: h('div', { class: 'campo' }, etiqueta, i, ayuda), leer: () => i.value };
    }
    case 'foto': {
      let nombre = valor || '';
      const prev = h('img', { alt: '' });
      const mostrar = () => {
        if (!nombre) return prev.removeAttribute('src');
        prev.onerror = () => { prev.onerror = null; prev.src = fotoRespaldo(nombre); };
        prev.src = fotoURL(nombre);
      };
      const texto = h('span', { class: 'archivo' }, nombre || 'Sin foto');
      const input = h('input', {
        id, type: 'file', accept: 'image/jpeg,image/png,image/webp', class: 'oculto',
        onchange: async () => {
          const f = input.files[0];
          if (!f) return;
          try {
            const bmp = await createImageBitmap(f);
            if (Math.max(bmp.width, bmp.height) < 1600) toast(`La foto mide ${bmp.width}×${bmp.height} px. Se ve mejor con al menos 1600 px.`, true);
            texto.textContent = 'Subiendo…';
            nombre = await api.subir(f);
            mostrar();
          } catch (e) { fallo(e); }
          texto.textContent = nombre || 'Sin foto';
          input.value = '';
        },
      });
      mostrar();
      return {
        el: h('div', { class: 'campo' }, etiqueta,
          h('div', { class: 'foto' }, prev, h('div', {}, texto, h('label', { class: 'btn sec', for: id }, nombre ? 'Cambiar foto' : 'Subir foto'), input)),
          h('small', { class: 'ayuda' }, 'JPG, PNG o WebP de al menos 1600 px. El sitio la optimiza solo.')),
        leer: () => nombre,
      };
    }
    case 'grupo': {
      const partes = def.campos.map(c => [c.name, campo(c, valor?.[c.name], ctx)]);
      return {
        el: h('fieldset', { class: 'campo grupo' }, h('legend', {}, def.label || ''), partes.map(p => p[1].el)),
        leer: () => Object.fromEntries(partes.map(([n, p]) => [n, p.leer()])),
      };
    }
    case 'lista': {
      const items = h('div', { class: 'items' });
      const filas = [];
      const nuevo = v => (def.item ? campo(def.item, v, ctx) : campo({ tipo: 'grupo', campos: def.campos }, v, ctx));
      const mover = (i, d) => { [filas[i], filas[i + d]] = [filas[i + d], filas[i]]; pintar(); };
      const pintar = () => items.replaceChildren(...filas.map((f, i) => h('div', { class: 'item' }, f.el,
        h('div', { class: 'item-acc' },
          boton('↑', () => mover(i, -1), { off: i === 0, titulo: 'Subir' }),
          boton('↓', () => mover(i, 1), { off: i === filas.length - 1, titulo: 'Bajar' }),
          boton('Quitar', () => { filas.splice(i, 1); pintar(); }, { cls: 'mini peligro' })))));
      (valor || []).forEach(v => filas.push(nuevo(v)));
      pintar();
      return {
        el: h('fieldset', { class: 'campo lista' }, h('legend', {}, def.label), items,
          boton('+ Agregar', () => { filas.push(nuevo(copia(def.nuevo))); pintar(); }, { cls: 'btn sec' }), ayuda),
        leer: () => filas.map(f => f.leer()),
      };
    }
    case 'servicios': {
      const marcas = (ctx.servicios || []).filter(d => d.url !== ctx.url)
        .map(d => [d, h('input', { type: 'checkbox', checked: (valor || []).includes(d.url) })]);
      return {
        el: h('fieldset', { class: 'campo' }, h('legend', {}, def.label),
          h('div', { class: 'opciones' }, marcas.map(([d, i]) => h('label', {}, i, d.nombre))), ayuda),
        leer: () => marcas.filter(([, i]) => i.checked).map(([d]) => d.url),
      };
    }
  }
  throw new Error('Tipo de campo desconocido: ' + def.tipo);
}

function formulario(campos, fila, ctx) {
  const partes = campos.map(c => [c.name, campo(c, fila[c.name], ctx)]);
  return {
    el: h('div', { class: 'form' }, partes.map(p => p[1].el)),
    leer: () => ({ ...fila, ...Object.fromEntries(partes.map(([n, p]) => [n, p.leer()])) }),
  };
}

function editor(main, { titulo, tabla, campos, fila, existente, ctx, volver }) {
  const f = formulario(campos, fila, { ...ctx, existente, url: fila.url });
  const guardar = async e => {
    const b = e.currentTarget;
    b.disabled = true;
    try {
      const datos = f.leer();
      if (!/^[a-z0-9-]+$/.test(datos.url)) throw new Error('La dirección (url) solo admite minúsculas, números y guiones.');
      await api.guardar(tabla, datos, !existente);
      listo('Guardado. Pulsa «Publicar cambios» cuando quieras verlo en el sitio.');
      volver();
    } catch (er) { fallo(er); b.disabled = false; }
  };
  main.replaceChildren(
    h('div', { class: 'cabeza' }, h('h1', {}, titulo), boton('← Volver', volver, { cls: 'btn sec' })),
    f.el,
    h('div', { class: 'barra' }, boton('Guardar', guardar, { cls: 'btn rojo' }), boton('Cancelar', volver, { cls: 'btn sec' })),
  );
  scrollTo(0, 0);
}

// ---------- vistas ----------

async function vistaServicios(main) {
  const servicios = await api.listar('servicios');
  const volver = () => vistaServicios(main);
  const abrir = (fila, existente) => editor(main, { titulo: existente ? `Editar ${fila.nombre}` : 'Nuevo servicio', tabla: 'servicios', campos: CAMPOS.servicios, fila, existente, ctx: { servicios }, volver });
  const borrar = async d => {
    if (!confirm(`¿Borrar el servicio «${d.nombre}»? Su página desaparece al publicar. No se puede deshacer.`)) return;
    try { await api.borrar('servicios', 'url', d.url); listo('Servicio borrado.'); volver(); } catch (e) { fallo(e); }
  };
  const vacio = { url: '', orden: servicios.length + 1, publicado: true, nombre: '', icono: 'i-design', resumen: '', titulo: '', titulo_em: '', texto: '', foto: '', alt: '',
    lista_titulo: '¿Qué incluye?', lista: [], cta: '', ocultar: [], catalogo_titulo: '', catalogo_titulo_em: '', catalogo_texto: '', piezas: [] };
  main.replaceChildren(
    h('div', { class: 'cabeza' }, h('h1', {}, 'Servicios'), boton('+ Nuevo servicio', () => abrir(copia(vacio), false), { cls: 'btn rojo' })),
    h('p', { class: 'intro' }, 'Cada servicio tiene su propia página en servicios/<url>.html y sale en el menú, en el inicio y en la página de servicios.'),
    h('div', { class: 'lista-filas' }, servicios.map(d => h('div', { class: 'fila' }, miniatura(d.foto),
      h('div', {}, h('b', {}, `${d.orden}. ${d.nombre}`), h('small', {}, `servicios/${d.url}.html`), ' ', !d.publicado && h('span', { class: 'chip apagado' }, 'No publicado')),
      h('div', { class: 'acc' },
        boton('Editar', () => abrir(copia(d), true)),
        h('a', { class: 'mini', href: `${SITIO}servicios/${d.url}.html`, target: '_blank', rel: 'noopener' }, 'Ver página'),
        boton('Borrar', () => borrar(d), { cls: 'mini peligro' }))))),
  );
}

async function vistaProyectos(main) {
  const proyectos = await api.listar('proyectos');
  const volver = () => vistaProyectos(main);
  const abrir = (fila, existente) => editor(main, { titulo: existente ? `Editar ${fila.nombre}` : 'Nuevo proyecto', tabla: 'proyectos', campos: CAMPOS.proyectos, fila, existente, volver });
  const borrar = async d => {
    if (!confirm(`¿Borrar el proyecto «${d.nombre}»? Desaparece del sitio al publicar. No se puede deshacer.`)) return;
    try { await api.borrar('proyectos', 'url', d.url); listo('Proyecto borrado.'); volver(); } catch (e) { fallo(e); }
  };
  const mover = async (i, d) => {
    [proyectos[i], proyectos[i + d]] = [proyectos[i + d], proyectos[i]];
    proyectos.forEach((f, k) => (f.orden = k + 1));
    try { await api.guardar('proyectos', proyectos); volver(); } catch (e) { fallo(e); }
  };
  const vacio = { url: '', orden: proyectos.length + 1, publicado: true, destacado: false, nombre: '', tipo: '', servicios: '', descripcion: '', foto_antes: '', foto_despues: '', despues: [], antes: [] };
  main.replaceChildren(
    h('div', { class: 'cabeza' }, h('h1', {}, 'Proyectos'), boton('+ Nuevo proyecto', () => abrir(copia(vacio), false), { cls: 'btn rojo' })),
    h('p', { class: 'intro' }, 'Todos salen juntos en la página de Proyectos, en este orden. Los marcados como «Destacado» salen también en el inicio. Sin fotos, el proyecto sale con el aviso «Fotos pendientes».'),
    h('div', { class: 'lista-filas' }, proyectos.map((d, i) => h('div', { class: 'fila' }, miniatura(d.foto_despues || d.despues[0]),
      h('div', {}, h('b', {}, d.nombre), h('small', {}, `${d.despues.length + d.antes.length} fotos`), ' ',
        d.destacado && h('span', { class: 'chip vivo' }, 'Destacado'), ' ',
        !d.publicado && h('span', { class: 'chip apagado' }, 'No publicado'), ' ',
        !d.despues.length && h('span', { class: 'chip apagado' }, 'Fotos pendientes')),
      h('div', { class: 'acc' },
        boton('Editar', () => abrir(copia(d), true)),
        boton('↑', () => mover(i, -1), { off: i === 0, titulo: 'Subir' }),
        boton('↓', () => mover(i, 1), { off: i === proyectos.length - 1, titulo: 'Bajar' }),
        boton('Borrar', () => borrar(d), { cls: 'mini peligro' }))))),
  );
}

async function vistaBlog(main) {
  const entradas = await api.listar('blog', 'fecha', true);
  const volver = () => vistaBlog(main);
  const abrir = (fila, existente) => editor(main, { titulo: existente ? 'Editar entrada' : 'Nueva entrada', tabla: 'blog', campos: CAMPOS.blog, fila, existente, volver });
  const borrar = async e => {
    if (!confirm(`¿Borrar la entrada «${e.titulo}»? Su página desaparece al publicar. No se puede deshacer.`)) return;
    try { await api.borrar('blog', 'url', e.url); listo('Entrada borrada.'); volver(); } catch (er) { fallo(er); }
  };
  const vacia = { url: '', publicado: false, fecha: hoy, autor: 'Equipo OMBU', categoria: '', lectura: 5, titulo: '', titulo_em: '', foto: '', alt: '', pie_foto: '', resumen: '', cuerpo: '' };
  main.replaceChildren(
    h('div', { class: 'cabeza' }, h('h1', {}, 'Blog'), boton('+ Nueva entrada', () => abrir(copia(vacia), false), { cls: 'btn rojo' })),
    h('p', { class: 'intro' }, 'Cada entrada tiene su propia página en blog/<url>.html y sale en el índice del blog, de la más nueva a la más vieja. Escríbela como borrador y actívala cuando esté lista; luego pulsa «Publicar cambios».'),
    entradas.length
      ? h('div', { class: 'lista-filas' }, entradas.map(e => h('div', { class: 'fila' }, miniatura(e.foto),
          h('div', {}, h('b', {}, e.titulo || '(sin título)'), h('small', {}, `${e.fecha} · blog/${e.url}.html`), ' ', h('span', { class: `chip ${e.publicado ? 'vivo' : 'apagado'}` }, e.publicado ? 'Publicada' : 'Borrador')),
          h('div', { class: 'acc' },
            boton('Editar', () => abrir(copia(e), true)),
            e.publicado && h('a', { class: 'mini', href: `${SITIO}blog/${e.url}.html`, target: '_blank', rel: 'noopener' }, 'Ver página'),
            boton('Borrar', () => borrar(e), { cls: 'mini peligro' })))))
      : h('p', { class: 'vacio' }, 'Todavía no hay entradas. Crea la primera con «+ Nueva entrada».'),
  );
}

// Textos de cada página, con las mismas secciones y en el mismo orden que en el sitio (esquema.js)
async function vistaPaginas(main) {
  const filas = await api.listar('paginas', 'id');
  const contenido = Object.fromEntries(filas.map(f => [f.id, f.contenido]));
  const volver = () => vistaPaginas(main);
  const abrir = pag => {
    const datos = copia(contenido[pag.id] || {});
    const partes = pag.secciones.map((sec, i) => {
      const f = formulario(sec.campos, datos[sec.id] || {}, {});
      return [sec.id, f, h('details', { class: 'seccion', open: i < 2 },
        h('summary', {}, sec.nombre),
        sec.ayuda && h('p', { class: 'ayuda sec-ayuda' }, sec.ayuda),
        f.el)];
    });
    const guardar = async e => {
      const b = e.currentTarget;
      b.disabled = true;
      try {
        for (const [id, f] of partes) datos[id] = f.leer();
        await api.guardar('paginas', { id: pag.id, contenido: datos });
        listo('Guardado. Pulsa «Publicar cambios» cuando quieras verlo en el sitio.');
        volver();
      } catch (er) { fallo(er); b.disabled = false; }
    };
    main.replaceChildren(
      h('div', { class: 'cabeza' }, h('h1', {}, pag.nombre),
        h('div', { class: 'acc-cabeza' },
          pag.ruta != null && h('a', { class: 'btn sec', href: SITIO + pag.ruta, target: '_blank', rel: 'noopener' }, 'Ver página'),
          boton('← Volver', volver, { cls: 'btn sec' }))),
      h('p', { class: 'intro' }, 'Las secciones están en el mismo orden en que se ven en la página. Ábrelas para editar.'),
      ...partes.map(p => p[2]),
      h('div', { class: 'barra' }, boton('Guardar', guardar, { cls: 'btn rojo' }), boton('Cancelar', volver, { cls: 'btn sec' })),
    );
    scrollTo(0, 0);
  };
  main.replaceChildren(
    h('div', { class: 'cabeza' }, h('h1', {}, 'Páginas')),
    h('p', { class: 'intro' }, 'Los textos y fotos de cada página del sitio. Los servicios, los proyectos y las entradas del blog tienen su propia sección.'),
    h('div', { class: 'lista-filas' }, PAGINAS.map(pag => h('div', { class: 'fila' },
      miniatura(contenido[pag.id]?.portada?.foto || contenido[pag.id]?.quienes?.foto || ''),
      h('div', {}, h('b', {}, pag.nombre), h('small', {}, pag.resumen || `${pag.secciones.length} ${pag.secciones.length === 1 ? 'sección' : 'secciones'} · /${pag.ruta}`)),
      h('div', { class: 'acc' }, boton('Editar', () => abrir(pag)),
        pag.ruta != null && h('a', { class: 'mini', href: SITIO + pag.ruta, target: '_blank', rel: 'noopener' }, 'Ver página'))))),
  );
}

async function vistaPublicaciones(main) {
  const publicaciones = await api.listar('publicaciones', 'pedido', true);
  main.replaceChildren(
    h('div', { class: 'cabeza' }, h('h1', {}, 'Publicaciones')),
    h('p', { class: 'intro' }, 'Cada vez que alguien pulsa «Publicar cambios». El sitio tarda 2 a 3 minutos en actualizarse.'),
    publicaciones.length
      ? h('div', { class: 'envoltura' }, h('table', { class: 'tabla' }, h('tr', {}, h('th', {}, 'Fecha'), h('th', {}, 'Quién'), h('th', {}, 'Estado')),
          publicaciones.slice(0, 20).map(p => h('tr', {}, h('td', {}, new Date(p.pedido).toLocaleString('es-CO')), h('td', {}, p.por), h('td', {}, p.estado)))))
      : h('p', { class: 'vacio' }, 'Todavía no se ha publicado desde el panel.'),
  );
}

async function vistaSolicitudes(main) {
  const filas = await api.listar('solicitudes', 'creado', true);
  const wa = n => h('a', { href: `https://wa.me/${(n || '').replace(/\D/g, '')}`, target: '_blank', rel: 'noopener' }, n);
  main.replaceChildren(
    h('div', { class: 'cabeza' }, h('h1', {}, 'Solicitudes')),
    h('p', { class: 'intro' }, 'Lo que llega por el formulario de contacto del sitio.'),
    filas.length
      ? h('div', { class: 'envoltura' }, h('table', { class: 'tabla' },
          h('tr', {}, ['Fecha', 'Nombre', 'Celular', 'Ciudad', 'Espacio', 'Mensaje'].map(t => h('th', {}, t))),
          filas.map(s => h('tr', {}, h('td', {}, new Date(s.creado).toLocaleString('es-CO')), h('td', {}, s.nombre), h('td', {}, s.whatsapp && wa(s.whatsapp)), h('td', {}, s.ciudad || ''), h('td', {}, s.tipo || ''), h('td', {}, s.mensaje || '')))))
      : h('p', { class: 'vacio' }, 'Aún no hay solicitudes.'),
  );
}

const VISTAS = [
  ['paginas', 'Páginas', vistaPaginas],
  ['servicios', 'Servicios', vistaServicios],
  ['proyectos', 'Proyectos', vistaProyectos],
  ['blog', 'Blog', vistaBlog],
  ['solicitudes', 'Solicitudes', vistaSolicitudes],
  ['publicaciones', 'Publicaciones', vistaPublicaciones],
];

async function ir() {
  const v = VISTAS.find(x => x[0] === location.hash.slice(1)) || VISTAS[0];
  document.querySelectorAll('.lado a').forEach(a => (a.dataset.k === v[0] ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current')));
  const main = document.getElementById('vista');
  main.replaceChildren(h('p', { class: 'cargando' }, 'Cargando…'));
  try { await v[2](main); } catch (e) { main.replaceChildren(h('p', { class: 'error' }, 'No se pudo cargar: ' + (e.message || e))); }
}

async function publicar(e) {
  const b = e.currentTarget;
  b.disabled = true;
  b.textContent = 'Publicando…';
  try { await api.publicar(); listo('Listo: el sitio se actualiza en 2 a 3 minutos.'); } catch (er) { fallo(er); }
  b.disabled = false;
  b.textContent = 'Publicar cambios';
}

function panel(usuario) {
  app.replaceChildren(
    h('header', { class: 'top' },
      h('div', { class: 'marca' }, h('img', { src: 'logo.svg', alt: '' }), h('b', {}, 'OMBU'), h('span', {}, 'Panel')),
      h('div', { class: 'top-acc' },
        DEMO && h('span', { class: 'chip' }, 'Modo demo'),
        h('span', { class: 'quien' }, usuario),
        h('a', { class: 'btn sec claro', href: SITIO, target: '_blank', rel: 'noopener' }, 'Ver sitio'),
        boton('Publicar cambios', publicar, { cls: 'btn rojo' }),
        sb && boton('Salir', () => sb.auth.signOut(), { cls: 'btn sec claro' }))),
    h('div', { class: 'cuerpo' },
      h('nav', { class: 'lado', 'aria-label': 'Secciones' }, VISTAS.map(([k, t]) => h('a', { href: '#' + k, 'data-k': k }, t))),
      h('main', { id: 'vista' })),
  );
  ir();
}
addEventListener('hashchange', () => document.getElementById('vista') && ir());

// ---------- acceso ----------

const tarjeta = (...hijos) => app.replaceChildren(h('div', { class: 'acceso' }, h('div', { class: 'tarjeta' }, h('img', { src: 'logo.svg', alt: '' }), ...hijos)));

function acceso(mensaje = '') {
  const email = h('input', { id: 'email', type: 'email', required: true, autocomplete: 'username', placeholder: 'tu@correo.com' });
  const clave = h('input', { id: 'clave', type: 'password', required: true, autocomplete: 'current-password' });
  const nota = h('p', { class: 'nota', role: 'status' }, mensaje);
  const entrar = h('button', { class: 'btn rojo', type: 'submit' }, 'Entrar');
  const olvide = boton('Olvidé mi contraseña', async () => {
    if (!email.value.trim()) { nota.textContent = 'Escribe tu correo arriba y vuelve a pulsar «Olvidé mi contraseña».'; return; }
    const { error } = await sb.auth.resetPasswordForEmail(email.value.trim().toLowerCase(), { redirectTo: location.origin + location.pathname });
    nota.textContent = error ? 'No pudimos enviar el correo. Intenta en unos minutos.' : 'Te enviamos un correo para crear una contraseña nueva.';
  }, { cls: 'enlace' });
  tarjeta(h('form', {
    style: 'display:grid;gap:14px',
    onsubmit: async e => {
      e.preventDefault();
      entrar.disabled = true;
      const { error } = await sb.auth.signInWithPassword({ email: email.value.trim().toLowerCase(), password: clave.value });
      entrar.disabled = false;
      if (error) nota.textContent = 'Correo o contraseña incorrectos.';
    },
  }, h('h1', {}, 'Panel OMBU'), h('p', {}, 'Entra con tu correo y tu contraseña.'),
    h('label', { class: 'lbl', for: 'email' }, 'Correo'), email,
    h('label', { class: 'lbl', for: 'clave' }, 'Contraseña'), clave,
    entrar, olvide, nota));
}

// Primera vez (invitación) u olvido: la persona crea su propia contraseña; nadie más la conoce
function crearClave(sesion, alTerminar) {
  const c1 = h('input', { id: 'c1', type: 'password', required: true, minLength: 8, autocomplete: 'new-password' });
  const c2 = h('input', { id: 'c2', type: 'password', required: true, minLength: 8, autocomplete: 'new-password' });
  const nota = h('p', { class: 'nota', role: 'status' });
  const guardar = h('button', { class: 'btn rojo', type: 'submit' }, 'Guardar contraseña');
  tarjeta(h('form', {
    style: 'display:grid;gap:14px',
    onsubmit: async e => {
      e.preventDefault();
      if (c1.value !== c2.value) { nota.textContent = 'Las dos contraseñas no coinciden.'; return; }
      guardar.disabled = true;
      const { error } = await sb.auth.updateUser({ password: c1.value });
      guardar.disabled = false;
      if (error) { nota.textContent = 'No se pudo guardar: ' + (error.message.includes('weak') || error.message.includes('least') ? 'usa al menos 8 caracteres, con letras y números.' : error.message); return; }
      alTerminar();
    },
  }, h('h1', {}, 'Crea tu contraseña'), h('p', {}, `Para ${sesion.user.email}. Usa al menos 8 caracteres, con letras y números. Con ella entrarás al panel de ahora en adelante.`),
    h('label', { class: 'lbl', for: 'c1' }, 'Contraseña nueva'), c1,
    h('label', { class: 'lbl', for: 'c2' }, 'Repítela'), c2, guardar, nota));
}

if (DEMO) panel('demo');
else if (!sb) {
  tarjeta(h('h1', {}, 'Panel OMBU'),
    h('p', {}, 'El panel está listo, pero falta conectar el proyecto de Supabase (panel/config.js).'),
    h('a', { class: 'btn rojo', href: '?demo' }, 'Ver el panel en modo demo'));
} else {
  let dentro = false, porCrear = CREAR_CLAVE;
  const entrar = async (sesion, evento) => {
    if (!sesion) { dentro = false; return acceso(); }
    if (porCrear || evento === 'PASSWORD_RECOVERY') {
      porCrear = false;
      return crearClave(sesion, () => entrar(sesion));
    }
    const { data: esEditor, error } = await sb.rpc('es_editor');
    if (error || !esEditor) {
      dentro = false;
      return tarjeta(h('h1', {}, 'Sin permiso'), h('p', {}, `El correo ${sesion.user.email} no está autorizado para editar. Pide que lo agreguen como editor.`), boton('Salir', () => sb.auth.signOut(), { cls: 'btn sec' }));
    }
    if (!dentro) { dentro = true; panel(sesion.user.email); }
  };
  // fuera del callback para no bloquear el cliente de Supabase
  sb.auth.onAuthStateChange((evento, sesion) => setTimeout(() => entrar(sesion, evento)));
}
