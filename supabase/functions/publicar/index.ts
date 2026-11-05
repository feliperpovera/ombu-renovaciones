// Botón «Publicar cambios» del panel: verifica que quien lo pide sea editor
// y le pide a GitHub que regenere el sitio (evento repository_dispatch «publicar»).
// Secretos de la función: GITHUB_TOKEN (token con permiso Contents: write sobre el repositorio)
// y GITHUB_REPO (ej. feliperpovera/ombu-renovaciones). SUPABASE_URL lo pone Supabase.
import { createClient } from 'npm:@supabase/supabase-js@2.117.2';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};
const respuesta = (cuerpo: unknown, status = 200) =>
  new Response(JSON.stringify(cuerpo), { status, headers: { ...cors, 'Content-Type': 'application/json' } });

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });

  // la clave pública llega en la cabecera «apikey» que manda el panel (sirve con claves nuevas y antiguas)
  const clave = req.headers.get('apikey') ?? Deno.env.get('SUPABASE_ANON_KEY') ?? '';
  const sb = createClient(Deno.env.get('SUPABASE_URL')!, clave, {
    global: { headers: { Authorization: req.headers.get('Authorization') ?? '' } },
  });
  const { data: { user } } = await sb.auth.getUser();
  const { data: editor } = await sb.rpc('es_editor');
  if (!user || !editor) return respuesta({ error: 'Sin permiso para publicar' }, 403);

  const gh = await fetch(`https://api.github.com/repos/${Deno.env.get('GITHUB_REPO')}/dispatches`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${Deno.env.get('GITHUB_TOKEN')}`,
      Accept: 'application/vnd.github+json',
      'User-Agent': 'ombu-panel',
    },
    body: JSON.stringify({ event_type: 'publicar', client_payload: { por: user.email } }),
  });
  const estado = gh.ok ? 'enviada' : `error ${gh.status}`;
  await sb.from('publicaciones').insert({ por: user.email, estado });
  return gh.ok ? respuesta({ ok: true }) : respuesta({ error: `GitHub respondió ${gh.status}` }, 502);
});
