// Pasa el contenido actual de contenido/ a Supabase, una sola vez, al crear el proyecto.
//   node herramientas/supabase/semilla.mjs  → escribe supabase/seed.sql
// Las fotos actuales ya están en fotos/ (repositorio); en Supabase solo quedan las que se suban desde el panel.
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';

const EDITORES = [['ombumercadeo@gmail.com', 'OMBU']];

const lit = v => `'${String(v).replace(/'/g, "''")}'`;
const valor = v => v === null ? 'null' : typeof v === 'object' ? `${lit(JSON.stringify(v))}::jsonb` : typeof v === 'string' ? lit(v) : String(v);
const leer = f => JSON.parse(readFileSync(f, 'utf8'));
const carpeta = c => readdirSync(c).filter(f => f.endsWith('.json')).sort().map(f => [f.replace('.json', ''), leer(`${c}/${f}`)]);
const fila = (tabla, o) => {
  const k = Object.keys(o);
  return `insert into public.${tabla} (${k.join(', ')}) values (${k.map(c => valor(o[c])).join(', ')}) on conflict do nothing;`;
};

const sql = [
  '-- Generado por herramientas/supabase/semilla.mjs con el contenido de contenido/',
  ...carpeta('contenido/paginas').map(([id, contenido]) => fila('paginas', { id, contenido })),
  '',
  ...carpeta('contenido/servicios').map(([, s]) => fila('servicios', s)),
  '',
  ...carpeta('contenido/proyectos').map(([, p]) => fila('proyectos', p)),
  '',
  ...carpeta('contenido/blog').map(([, e]) => fila('blog', e)),
  '',
  '-- Editores del panel',
  ...EDITORES.map(([email, nombre]) => fila('editores', { email, nombre })),
  '',
].join('\n');
writeFileSync('supabase/seed.sql', sql);
console.log('supabase/seed.sql listo');
