-- OMBU · esquema del contenido editable desde /admin
-- Lectura pública del contenido publicado (la usa el generador del sitio).
-- Escritura solo para correos que estén en la tabla «editores».

-- ---------- Quién puede editar ----------

create table public.editores (
  email text primary key check (email = lower(email)),
  nombre text not null default '',
  creado timestamptz not null default now()
);
comment on table public.editores is 'Correos autorizados para editar desde el panel.';

create function public.es_editor()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (select 1 from public.editores e where e.email = lower(auth.jwt() ->> 'email'));
$$;
revoke execute on function public.es_editor() from public, anon;
grant execute on function public.es_editor() to authenticated;

-- ---------- Contenido ----------

create table public.paginas (
  id text primary key,
  contenido jsonb not null default '{}'::jsonb,
  actualizado timestamptz not null default now()
);
comment on table public.paginas is 'Textos de cada página. Las secciones están en panel/esquema.js.';

create table public.servicios (
  url text primary key check (url ~ '^[a-z0-9-]+$'),
  orden int not null default 0,
  publicado boolean not null default true,
  nombre text not null,
  icono text not null default 'i-design',
  resumen text not null default '',
  titulo text not null default '',
  titulo_em text not null default '',
  texto text not null default '',
  foto text not null default '',
  alt text not null default '',
  lista_titulo text not null default '',
  lista jsonb not null default '[]'::jsonb,
  cta text not null default '',
  ocultar jsonb not null default '[]'::jsonb,
  catalogo_titulo text not null default '',
  catalogo_titulo_em text not null default '',
  catalogo_texto text not null default '',
  piezas jsonb not null default '[]'::jsonb,
  actualizado timestamptz not null default now()
);

create table public.proyectos (
  url text primary key check (url ~ '^[a-z0-9-]+$'),
  orden int not null default 0,
  publicado boolean not null default true,
  destacado boolean not null default false,
  nombre text not null,
  tipo text not null default '',
  servicios text not null default '',
  descripcion text not null default '',
  foto_antes text not null default '',
  foto_despues text not null default '',
  despues jsonb not null default '[]'::jsonb,
  antes jsonb not null default '[]'::jsonb,
  actualizado timestamptz not null default now()
);

create table public.blog (
  url text primary key check (url ~ '^[a-z0-9-]+$'),
  publicado boolean not null default false,
  fecha date not null default current_date,
  autor text not null default 'Equipo OMBU',
  categoria text not null default '',
  lectura int not null default 5,
  titulo text not null default '',
  titulo_em text not null default '',
  foto text not null default '',
  alt text not null default '',
  pie_foto text not null default '',
  resumen text not null default '',
  cuerpo text not null default '',
  actualizado timestamptz not null default now()
);

create table public.solicitudes (
  id bigint generated always as identity primary key,
  creado timestamptz not null default now(),
  origen text not null default 'contacto',
  nombre text not null check (char_length(nombre) between 1 and 200),
  whatsapp text check (char_length(whatsapp) <= 40),
  ciudad text check (char_length(ciudad) <= 120),
  tipo text check (char_length(tipo) <= 120),
  mensaje text check (char_length(mensaje) <= 4000)
);
comment on table public.solicitudes is 'Lo que llega por el formulario de contacto del sitio.';

create table public.publicaciones (
  id bigint generated always as identity primary key,
  pedido timestamptz not null default now(),
  por text not null,
  estado text not null
);
comment on table public.publicaciones is 'Historial del botón «Publicar cambios» del panel.';

-- «actualizado» al día en cada cambio
create function public.marcar_actualizado()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.actualizado := now();
  return new;
end;
$$;

create trigger paginas_actualizado before update on public.paginas for each row execute function public.marcar_actualizado();
create trigger servicios_actualizado before update on public.servicios for each row execute function public.marcar_actualizado();
create trigger proyectos_actualizado before update on public.proyectos for each row execute function public.marcar_actualizado();
create trigger blog_actualizado before update on public.blog for each row execute function public.marcar_actualizado();

-- ---------- Seguridad (RLS) ----------

alter table public.editores enable row level security;
alter table public.paginas enable row level security;
alter table public.servicios enable row level security;
alter table public.proyectos enable row level security;
alter table public.blog enable row level security;
alter table public.solicitudes enable row level security;
alter table public.publicaciones enable row level security;

-- editores: cada quien solo ve su propia fila (para saber si tiene permiso)
create policy "ver mi fila de editor" on public.editores for select to authenticated
  using (email = lower((select auth.jwt() ->> 'email')));

-- contenido: lectura pública; escritura de editores
create policy "leer paginas" on public.paginas for select to anon, authenticated using (true);
create policy "crear paginas" on public.paginas for insert to authenticated with check ((select public.es_editor()));
create policy "editar paginas" on public.paginas for update to authenticated
  using ((select public.es_editor())) with check ((select public.es_editor()));

create policy "leer servicios publicados" on public.servicios for select to anon, authenticated
  using (publicado or (select public.es_editor()));
create policy "crear servicios" on public.servicios for insert to authenticated with check ((select public.es_editor()));
create policy "editar servicios" on public.servicios for update to authenticated
  using ((select public.es_editor())) with check ((select public.es_editor()));
create policy "borrar servicios" on public.servicios for delete to authenticated using ((select public.es_editor()));

create policy "leer proyectos publicados" on public.proyectos for select to anon, authenticated
  using (publicado or (select public.es_editor()));
create policy "crear proyectos" on public.proyectos for insert to authenticated with check ((select public.es_editor()));
create policy "editar proyectos" on public.proyectos for update to authenticated
  using ((select public.es_editor())) with check ((select public.es_editor()));
create policy "borrar proyectos" on public.proyectos for delete to authenticated using ((select public.es_editor()));

create policy "leer entradas publicadas" on public.blog for select to anon, authenticated
  using (publicado or (select public.es_editor()));
create policy "crear entradas" on public.blog for insert to authenticated with check ((select public.es_editor()));
create policy "editar entradas" on public.blog for update to authenticated
  using ((select public.es_editor())) with check ((select public.es_editor()));
create policy "borrar entradas" on public.blog for delete to authenticated using ((select public.es_editor()));

-- solicitudes: cualquiera puede enviar; solo editores leen
create policy "enviar solicitud" on public.solicitudes for insert to anon, authenticated with check (true);
create policy "leer solicitudes" on public.solicitudes for select to authenticated using ((select public.es_editor()));

-- publicaciones: solo editores
create policy "registrar publicacion" on public.publicaciones for insert to authenticated with check ((select public.es_editor()));
create policy "ver publicaciones" on public.publicaciones for select to authenticated using ((select public.es_editor()));

-- ---------- Fotos (Storage) ----------

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('fotos', 'fotos', true, 15728640, array['image/jpeg', 'image/png', 'image/webp']);

create policy "subir fotos" on storage.objects for insert to authenticated
  with check (bucket_id = 'fotos' and (select public.es_editor()));
create policy "cambiar fotos" on storage.objects for update to authenticated
  using (bucket_id = 'fotos' and (select public.es_editor()));
create policy "borrar fotos" on storage.objects for delete to authenticated
  using (bucket_id = 'fotos' and (select public.es_editor()));
