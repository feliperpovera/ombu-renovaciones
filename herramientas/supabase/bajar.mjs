// Baja el contenido publicado de Supabase a contenido/ (mismo formato que usa generar.py)
// y las fotos que falten a fotos/. Lo corre la acción de GitHub antes de generar el sitio;
// así contenido/ queda como copia versionada de la base.
// Uso: SUPABASE_URL=… SUPABASE_ANON_KEY=… node herramientas/supabase/bajar.mjs
import { existsSync, readdirSync, rmSync, writeFileSync } from 'node:fs';

const { SUPABASE_URL: url, SUPABASE_ANON_KEY: clave } = process.env;
if (!url || !clave) {
  console.log('Supabase no está conectado: se usa contenido/ tal como está.');
  process.exit(0);
}

const leer = async (tabla, consulta) => {
  const r = await fetch(`${url}/rest/v1/${tabla}?${consulta}`, { headers: { apikey: clave, Authorization: `Bearer ${clave}` } });
  if (!r.ok) throw new Error(`${tabla}: ${r.status} ${await r.text()}`);
  return r.json();
};
const guardar = (ruta, datos) => writeFileSync(ruta, JSON.stringify(datos, null, 2) + '\n');
const sin = (o, ...claves) => Object.fromEntries(Object.entries(o).filter(([k]) => !claves.includes(k)));

const paginas = await leer('paginas', 'select=id,contenido');
const servicios = await leer('servicios', 'select=*&publicado=is.true&order=orden');
const proyectos = await leer('proyectos', 'select=*&publicado=is.true&order=orden');
const blog = await leer('blog', 'select=*&publicado=is.true&order=fecha.desc');

for (const p of paginas) guardar(`contenido/paginas/${p.id}.json`, p.contenido);

const espejo = (carpeta, filas) => {
  const vivos = new Set(filas.map(f => f.url + '.json'));
  for (const f of readdirSync(carpeta)) if (f.endsWith('.json') && !vivos.has(f)) rmSync(`${carpeta}/${f}`);
  for (const f of filas) guardar(`${carpeta}/${f.url}.json`, sin(f, 'actualizado'));
};
espejo('contenido/servicios', servicios);
espejo('contenido/proyectos', proyectos);
espejo('contenido/blog', blog);

// fotos: cualquier campo «foto…», las listas de proyectos y las que estén dentro de un texto
const fotosDe = o => !o || typeof o !== 'object' ? [] : Object.entries(o).flatMap(([k, v]) => {
  if (typeof v === 'string') return /^foto/.test(k) ? [v] : [...v.matchAll(/!\[[^\]]*\]\((\S+?)[\s)]/g)].map(m => m[1]);
  if ((k === 'despues' || k === 'antes') && Array.isArray(v)) return v;
  return fotosDe(v);
});
const usadas = new Set([...paginas, ...servicios, ...proyectos, ...blog].flatMap(fotosDe).filter(Boolean));
let nuevas = 0;
for (const f of usadas) {
  if (existsSync('fotos/' + f)) continue;
  const r = await fetch(`${url}/storage/v1/object/public/fotos/${encodeURIComponent(f)}`);
  if (!r.ok) throw new Error(`No se pudo bajar la foto ${f}: ${r.status}`);
  writeFileSync('fotos/' + f, Buffer.from(await r.arrayBuffer()));
  nuevas++;
}
console.log(`Supabase → contenido: ${paginas.length} páginas, ${servicios.length} servicios, ${proyectos.length} proyectos, ${blog.length} entradas de blog, ${nuevas} fotos nuevas`);
