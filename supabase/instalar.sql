-- Pegar completo en Supabase → SQL Editor y ejecutar una sola vez.

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

-- Generado por herramientas/supabase/semilla.mjs con el contenido de contenido/
insert into public.paginas (id, contenido) values ('aviso-de-privacidad', '{"documento":{"titulo":"Aviso","titulo_em":"de privacidad","texto":"El resumen de cómo tratamos tus datos personales, según el artículo 15 del Decreto 1377 de 2013.","vigencia":"3 de noviembre de 2026","cuerpo":"## Responsable\n\n[[responsable]]\n\n## Qué hacemos con tus datos\n\nRecolectamos tu nombre, apellido, celular, ciudad y la información de tu proyecto para responder tu solicitud, asesorarte, preparar tu cotización, coordinar tu proyecto y, si nos das permiso, enviarte novedades de OMBU.\n\n## Tus derechos\n\nPuedes conocer, actualizar, corregir y pedir que eliminemos tus datos, revocar tu autorización, pedir prueba de ella y presentar quejas ante la Superintendencia de Industria y Comercio. Las preguntas sobre datos sensibles o de menores de edad son de respuesta opcional.\n\n## Cómo ejercerlos\n\nEscríbenos al correo o por WhatsApp. Respondemos consultas en máximo 10 días hábiles y reclamos en máximo 15 días hábiles.\n\n## Política completa\n\nConsulta todos los detalles en nuestra [Política de tratamiento de datos personales](politica-de-datos.html)."}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('blog', '{"seo":{"titulo":"Blog · OMBU Renovaciones","descripcion":"Ideas, inspiración y conocimiento para transformar espacios: diseño, renovación, materiales y construcción."},"portada":{"titulo":"Ideas, inspiración y conocimiento","titulo_em":"para transformar espacios.","texto":"Diseño e interiorismo, consejos para renovar, materiales, procesos de construcción y tendencias."}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('contacto', '{"seo":{"titulo":"Contacto · OMBU Renovaciones","descripcion":"Cuéntanos tu idea y nuestro equipo se pondrá en contacto contigo. La primera reunión es gratuita."},"portada":{"titulo":"Hablemos del espacio","titulo_em":"que tienes en mente.","texto":"Toda transformación comienza con una idea. Cuéntanos la tuya y nuestro equipo se pondrá en contacto contigo."},"formulario":{"titulo":"Cuéntanos de tu proyecto","ayuda":"Toma menos de un minuto.","pregunta_espacio":"¿Qué espacio quieres transformar?","opciones":["Vivienda","Oficina","Local comercial","Otro"],"idea":"Cuéntanos tu idea","idea_ejemplo":"Ej.: renovar cocina y baños, cambiar pisos…","boton":"Enviar mi proyecto","nota":"Se abrirá WhatsApp con tu mensaje listo para enviar.","gracias_titulo":"¡Gracias por compartir tu idea!","gracias_texto":"Recibimos tu información y nuestro equipo se pondrá en contacto contigo."}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('general', '{"contacto":{"whatsapp":"+57 310 599 6809","mensaje_whatsapp":"Hola OMBU, quiero cotizar la renovación de mi espacio.","instagram_url":"https://www.instagram.com/ombu.renovaciones/","instagram_txt":"@ombu.renovaciones","facebook_url":"https://www.facebook.com/share/1AA67nPHKe/","ubicacion":"Medellín, Antioquia"},"legal":{"responsable":"OMBU Renovaciones","nit":"","direccion":"","correo":""},"pie":{"frase":"Una vida detrás","frase_em":"de cada puerta.","derechos":"© 2026 OMBU Renovaciones · Medellín, Antioquia"},"banda":{"titulo":"Tu próxima vida empieza","titulo_em":"con una conversación.","texto":"Cuéntanos qué tienes en mente. Nuestro equipo te ayudará a dar el primer paso.","boton":"Hablemos de tu proyecto","foto":"palo-alto-d01.webp"},"atributos":{"lista":[{"titulo":"Confianza y respaldo","texto":"Contratos, pólizas y procesos que aportan seguridad a cada proyecto."},{"titulo":"Diseño a la medida","texto":"Soluciones pensadas alrededor de tus necesidades."},{"titulo":"Experiencia comprobada","texto":"Proyectos y transformaciones que muestran nuestro trabajo."},{"titulo":"Acompañamiento cercano","texto":"Profesionales presentes en cada etapa."},{"titulo":"Equipo propio","texto":"Integramos diseño, interiorismo, construcción, mano de obra y logística."}]},"pasos":{"lista":[{"titulo":"Nos cuentas tu idea","texto":"Nos reunimos para conocer tus necesidades, expectativas y el espacio que quieres transformar."},{"titulo":"Diseñamos a tu medida","texto":"Desarrollamos una propuesta personalizada, ajustamos los detalles y definimos el presupuesto."},{"titulo":"Construimos con respaldo","texto":"Nuestro equipo ejecuta el proyecto con acompañamiento, seguimiento y reportes periódicos."},{"titulo":"Entregamos lo acordado","texto":"Revisamos los detalles finales y hacemos entrega del proyecto terminado."}]},"testimonios":{"eyebrow":"Testimonios","titulo":"Ellos ya confiaron","titulo_em":"en OMBU","lista":[{"nombre":"Emilio Ortega","detalle":"Renovación total de apartamento","cita":"«Hice la renovación total de mi apartamento con Ombu y, sinceramente, fue una de las mejores decisiones que he tomado.»","texto":"Desde el primer día se encargaron absolutamente de todo. Yo solo conté cómo quería mi espacio y ellos se encargaron de convertir esa idea en algo incluso mejor de lo que imaginé. Los acabados, los materiales y los detalles son de primera. Se nota el cuidado y la calidad en cada rincón. Recomiendo a Ombu sin dudarlo. Son profesionales, cumplidos y el resultado final habla por ellos."},{"nombre":"Laura Duran","detalle":"Oficina y segundo piso","cita":"«Nuestra experiencia con Ombu fue increíble.»","texto":"Decidimos renovar completamente la oficina y hacer un segundo piso. Siempre nos sentimos acompañados en todo el proceso de renovación, desde escoger el diseño hasta los últimos detalles. ¡Definitivamente la mejor opción que pudimos hacer! ¡Increíble todo el proceso con ellos! Gracias Ombu 🙌🏻"},{"nombre":"Juan Miguel Jaramillo","detalle":"Cliente OMBU","cita":"«Me fue muy bien.»","texto":"Un proceso muy eficiente, los materiales excelentes y los acabados muy bonitos, todo muy rápido, muy buen presupuesto. Todo 100/100. Muy contento con el resultado."},{"nombre":"Susana Ospina","detalle":"Remodelación completa de apartamento","cita":"«Hice la remodelación completa de mi apartamento con Ombu. Fue la mejor decisión que pude haber tomado.»","texto":"Ellos se encargaron de TODO. Yo solo tuve que soñar lo que quería y ellos lo hicieron realidad. Lo mejor de todo es que los materiales son de alta calidad. Los recomiendo 100%."}]},"faq":{"eyebrow":"Preguntas frecuentes","titulo":"Lo que más","titulo_em":"nos preguntan","lista":[{"pregunta":"¿La primera reunión tiene algún costo?","respuesta":"No. Nuestra primera reunión es gratuita y nos permite conocer tu idea, entender lo que necesitas y conversar sobre las posibilidades de tu proyecto."},{"pregunta":"¿Cuánto tiempo tarda un proyecto?","respuesta":"Depende del alcance y las necesidades de cada espacio. Como referencia, la etapa de diseño puede tomar entre 30 y 45 días, mientras que una obra puede tardar entre 90 y 180 días."},{"pregunta":"¿El precio de mi proyecto puede cambiar?","respuesta":"Trabajamos con presupuestos cerrados. El valor cotizado se mantiene de acuerdo con el alcance aprobado inicialmente."},{"pregunta":"¿De qué depende el costo de un proyecto?","respuesta":"El presupuesto depende de las características de cada intervención, incluyendo materiales seleccionados, áreas que se van a transformar, iluminación y posibles redistribuciones del espacio."}]}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('inicio', '{"seo":{"titulo":"OMBU Renovaciones · Diseño y construcción de espacios en Medellín","descripcion":"Diseñamos, transformamos y construimos viviendas, oficinas y espacios comerciales en Medellín, con un equipo propio de la primera idea a la entrega."},"portada":{"eyebrow":"Diseño y construcción · Medellín","titulo":"Tú sueñas el espacio.","titulo_em":"Nosotros nos encargamos de todo.","texto":"Diseñamos y construimos espacios que se adaptan a ti. Con un equipo propio que te acompaña desde la primera idea hasta la entrega final.","boton":"Empezar mi proyecto","boton2":"Ver proyectos","garantias":["Equipo propio","Presupuestos cerrados","Primera reunión gratis"],"foto":"hero.webp","alt":"Sala y cocina renovadas por OMBU con paneles de madera, piso laminado y ventanales hacia la naturaleza"},"sobre":{"eyebrow":"Sobre OMBU","titulo":"Espacios pensados para ti.","titulo_em":"Procesos respaldados por expertos.","parrafos":["Somos una empresa de diseño y construcción especializada en renovar viviendas, oficinas y espacios comerciales.","Creemos que cada espacio debe responder a quienes lo habitan. Por eso, combinamos **diseño personalizado, conocimiento técnico y un equipo propio** de profesionales para hacer realidad cada proyecto."],"boton":"Conoce OMBU","foto":"fondo.webp","alt":"Sala renovada con muro revestido en madera, sofá claro y comedor al fondo"},"servicios":{"eyebrow":"Nuestros servicios","titulo":"Todo lo que necesitas","titulo_em":"para transformar tu espacio.","boton":"Conoce nuestros servicios"},"proceso":{"eyebrow":"Cómo trabajamos","titulo":"Un solo equipo.","titulo_em":"Un proceso pensado para ti.","texto":"De la primera conversación a la entrega final, te acompañamos en cada decisión.","boton":"Conoce nuestro proceso"},"proyectos":{"eyebrow":"Proyectos destacados","titulo":"Los espacios cuentan","titulo_em":"nuestra historia.","texto":"Cada proyecto es una oportunidad para transformar ideas en espacios reales. Explora algunos de nuestros trabajos.","cifra":"+80","cifra_txt":"proyectos","boton":"Ver todos los proyectos"},"por_que":{"eyebrow":"¿Por qué elegir OMBU?","titulo":"La tranquilidad de estar","titulo_em":"en buenas manos."},"blog":{"eyebrow":"Blog","titulo":"Ideas para","titulo_em":"tu próximo espacio","enlace":"Ver todo el blog"}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('nosotros', '{"seo":{"titulo":"Nosotros · OMBU Renovaciones","descripcion":"Somos una empresa de diseño y construcción con equipo propio. Conoce quiénes somos y cómo trabajamos."},"portada":{"titulo":"Diseñamos espacios.","titulo_em":"Construimos confianza.","texto":"En OMBU creemos que un espacio bien pensado puede transformar la manera en que vivimos y trabajamos."},"quienes":{"eyebrow":"Quiénes somos","titulo":"Un solo equipo,","titulo_em":"de la idea a la entrega.","parrafos":["Somos una empresa de diseño y construcción enfocada en renovar viviendas, oficinas y locales comerciales para convertirlos en espacios funcionales, personalizados y alineados con las necesidades de cada cliente.","Contamos con un **equipo propio de diseño, interiorismo, construcción, mano de obra y logística.** Esto nos permite mantener el control del proceso y ofrecer acompañamiento desde el inicio hasta la entrega."],"foto":"fondo.webp","alt":"Sala renovada por OMBU con muro revestido en madera"},"diferencia":{"eyebrow":"Por qué elegirnos","titulo":"Lo que nos","titulo_em":"diferencia."},"proceso":{"eyebrow":"Cómo trabajamos","titulo":"De una idea a un espacio","titulo_em":"hecho realidad.","texto":"Creemos en procesos claros, comunicación cercana y decisiones bien acompañadas. Así transformamos tu proyecto paso a paso.","etapas":[{"titulo":"Nos conocemos","pasos":["Nos compartes tu idea o necesidad.","Nuestro equipo comercial te recibe.","Agendamos una reunión para conocerte.","Preparamos un plan de trabajo personalizado."]},{"titulo":"Diseñamos contigo","pasos":["Realizamos el levantamiento del espacio y conocemos tus expectativas.","Desarrollamos una propuesta inicial.","Revisamos y ajustamos el diseño contigo.","Aprobamos los diseños y el presupuesto."]},{"titulo":"Hacemos realidad el proyecto","pasos":["Iniciamos la etapa de obra.","Ejecutamos el proyecto con director de obra, líder de ejecución, residente de obra y personal de ejecución. Compartimos informes semanales y programamos visitas de seguimiento con el cliente."]},{"titulo":"Entregamos","pasos":["Realizamos la entrega final del proyecto."]}]},"equipo":{"eyebrow":"Nuestro equipo","titulo":"Detrás de cada espacio,","titulo_em":"hay un equipo.","texto":"Diseñadores, profesionales de construcción y personal operativo trabajan de manera coordinada para que cada etapa del proyecto avance bajo una misma visión.","fotos":[{"foto":"","texto":"Reuniones de diseño"},{"foto":"","texto":"Visitas de obra"},{"foto":"","texto":"Ejecución"}]},"cta":{"boton":"Quiero empezar mi proyecto"}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('politica-de-cookies', '{"documento":{"titulo":"Política","titulo_em":"de cookies","texto":"Qué guarda este sitio en tu navegador, para qué y cómo puedes cambiar tu elección.","vigencia":"3 de noviembre de 2026","cuerpo":"## 1. Qué son\n\nLas cookies y el almacenamiento local son pequeños archivos que un sitio guarda en tu navegador para recordar información entre visitas.\n\n## 2. Qué usamos hoy\n\n- **ombu-cookies** (necesaria, almacenamiento local): recuerda las preferencias de cookies que elegiste. Dura hasta que la borres de tu navegador.\n\nHoy este sitio no usa cookies de analítica ni de marketing, ni carga herramientas de terceros que te rastreen.\n\n## 3. Categorías\n\n- **Necesarias:** hacen funcionar el sitio y recuerdan tus preferencias. Siempre están activas.\n- **Analítica:** nos dirían qué páginas se visitan para mejorar el sitio. Solo se activarían si las aceptas.\n- **Marketing:** permitirían mostrarte anuncios de OMBU en otras plataformas. Solo se activarían si las aceptas.\n\nSi en el futuro activamos analítica o marketing, actualizaremos esta tabla antes de hacerlo.\n\n## 4. Enlaces a otras plataformas\n\nAl tocar los botones de WhatsApp, Instagram o Facebook sales de este sitio. Esas plataformas usan sus propias cookies según sus políticas.\n\n## 5. Cómo cambiar tu elección\n\nPuedes cambiar tu elección cuando quieras con este botón o desde el pie de página. También puedes borrar o bloquear las cookies en la configuración de tu navegador.\n\n[[cookies]]\n\n## 6. Más información\n\nConsulta nuestra [Política de tratamiento de datos personales](politica-de-datos.html)."}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('politica-de-datos', '{"documento":{"titulo":"Política de tratamiento","titulo_em":"de datos personales","texto":"Cómo recolectamos, usamos y protegemos tu información, y cómo puedes conocerla, actualizarla o pedir que la eliminemos.","vigencia":"3 de noviembre de 2026","cuerpo":"## 1. Responsable del tratamiento\n\n[[responsable]]\n\n## 2. Marco legal\n\nEsta política cumple la Ley Estatutaria 1581 de 2012, el Decreto 1377 de 2013 (compilado en el Decreto Único 1074 de 2015) y demás normas colombianas sobre protección de datos personales.\n\n## 3. Qué datos recolectamos\n\n- **Datos de contacto:** nombre, apellido, número de celular y ciudad que escribes en el formulario o nos envías por WhatsApp.\n- **Datos del proyecto:** tipo de espacio, ideas, fotos, planos y medidas que decidas compartir.\n- **Datos de navegación:** tus preferencias de cookies, guardadas en tu propio navegador.\n\nNo pedimos datos sensibles ni datos de menores de edad.\n\n## 4. Para qué los usamos\n\n- Responder tu solicitud, asesorarte y preparar tu cotización.\n- Coordinar visitas, diseño, ejecución y entrega de tu proyecto.\n- Enviarte información sobre el estado de tu obra y garantías.\n- Enviarte novedades de OMBU, solo si nos das permiso. Puedes retirarlo cuando quieras.\n- Cumplir obligaciones legales, contables y tributarias.\n\n## 5. Autorización\n\nAl marcar la casilla de autorización del formulario, o al escribirnos por WhatsApp, nos autorizas a tratar tus datos para las finalidades anteriores. Guardamos prueba de esa autorización mientras dure la relación contigo.\n\n## 6. Tus derechos\n\nComo titular de los datos puedes:\n\n- Conocer, actualizar y corregir tus datos.\n- Pedir prueba de la autorización que nos diste.\n- Saber cómo hemos usado tus datos.\n- Revocar la autorización o pedir que eliminemos tus datos, cuando no exista un deber legal o contractual de conservarlos.\n- Presentar quejas ante la Superintendencia de Industria y Comercio (SIC).\n- Acceder gratis a tus datos personales.\n\n## 7. Cómo ejercer tus derechos\n\nEscríbenos al correo o por WhatsApp con tu nombre, número de contacto y lo que necesitas.\n\n- **Consultas:** respondemos en máximo 10 días hábiles. Si necesitamos más tiempo te avisamos, y nunca serán más de 5 días hábiles adicionales.\n- **Reclamos** (corrección, actualización, eliminación o revocatoria): respondemos en máximo 15 días hábiles, prorrogables hasta 8 días hábiles más con aviso previo.\n\nAntes de acudir a la SIC debes haber presentado tu consulta o reclamo ante nosotros.\n\n## 8. Con quién compartimos tus datos\n\nNo vendemos ni alquilamos tus datos. Los compartimos solo con quienes nos ayudan a prestar el servicio (por ejemplo, proveedores y contratistas de tu obra) y bajo deber de confidencialidad. Las conversaciones por WhatsApp pasan por los servidores de Meta Platforms, que pueden estar fuera de Colombia.\n\n## 9. Seguridad y conservación\n\nAplicamos medidas razonables para evitar pérdida, uso o acceso no autorizado a tus datos. Los conservamos mientras dure la relación contigo y el tiempo que exija la ley.\n\n## 10. Cookies\n\nLo que guarda el sitio en tu navegador está explicado en nuestra [Política de cookies](politica-de-cookies.html).\n\n## 11. Cambios a esta política\n\nSi cambiamos esta política publicaremos la nueva versión en esta página con su fecha de vigencia. Si el cambio afecta las finalidades, te pediremos una nueva autorización."}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('proyectos', '{"seo":{"titulo":"Proyectos · OMBU Renovaciones","descripcion":"Más de 80 proyectos de diseño y construcción. Mira el antes y el después de las obras de OMBU."},"portada":{"titulo":"Espacios que hablan","titulo_em":"por nosotros.","texto":"Detrás de cada proyecto hay una idea, un proceso y una transformación. Desliza cada foto para comparar el antes y el después, y toca el nombre para ver todas las fotos.","cifra":"+80","cifra_txt":"proyectos"},"cta":{"boton":"Quiero transformar mi espacio"}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('servicios', '{"seo":{"titulo":"Servicios · OMBU Renovaciones","descripcion":"Diseño, construcción, mobiliario e interventoría para viviendas, oficinas y espacios comerciales en Medellín."},"portada":{"titulo":"Soluciones integrales","titulo_em":"para cada espacio.","texto":"Diseño, construcción, mobiliario e interventoría con un mismo equipo. Elige por dónde empezar o combínalos en un solo proyecto."},"lista":{"eyebrow":"Servicios","titulo":"Todo lo que necesitas","titulo_em":"para transformar tu espacio."},"otros":{"eyebrow":"También hacemos","titulo":"Otros servicios","titulo_em":"que se complementan."}}'::jsonb) on conflict do nothing;
insert into public.paginas (id, contenido) values ('terminos-y-condiciones', '{"documento":{"titulo":"Términos y condiciones","titulo_em":"de uso del sitio","texto":"Las reglas para usar este sitio web y lo que puedes esperar de la información que publicamos.","vigencia":"3 de noviembre de 2026","cuerpo":"## 1. Quiénes somos\n\nEste sitio pertenece a OMBU Renovaciones, empresa de diseño y construcción con domicilio en Medellín, Colombia.\n\n[[responsable]]\n\n## 2. Aceptación\n\nAl navegar por este sitio o enviar el formulario de contacto aceptas estos términos. Si no estás de acuerdo con ellos, te pedimos no usar el sitio.\n\n## 3. Uso del sitio\n\nPuedes usar el sitio para conocer nuestros servicios y proyectos y para contactarnos. No está permitido:\n\n- Usarlo para fines ilegales o que afecten derechos de otras personas.\n- Enviar información falsa o hacerte pasar por otra persona.\n- Intentar dañar, sobrecargar o acceder sin permiso a partes del sitio o de sus servidores.\n- Copiar o reutilizar el contenido con fines comerciales sin nuestra autorización.\n\n## 4. Información del sitio\n\nLos textos, fotografías y proyectos del sitio muestran trabajos realizados y tienen fines informativos. No son una oferta comercial vinculante.\n\nLos tiempos que mencionamos (por ejemplo, de 30 a 45 días para diseño o de 90 a 180 días para obra) son referencias. El alcance, el valor, los plazos y las garantías de cada proyecto se definen en la cotización y en el contrato escrito que firmamos contigo.\n\n## 5. Cotizaciones y contratos\n\nLa primera reunión es gratuita. Enviar el formulario o escribirnos por WhatsApp no crea ningún compromiso para ninguna de las partes. Cada proyecto se rige por su propio contrato, que prevalece sobre lo publicado en este sitio.\n\n## 6. Propiedad intelectual\n\nLa marca OMBU, el logo, los textos, las fotografías, los diseños y demás contenidos del sitio pertenecen a OMBU Renovaciones o se usan con autorización de sus titulares. Están protegidos por la Ley 23 de 1982, la Decisión Andina 351 de 1993 y demás normas de derechos de autor y propiedad industrial. No puedes reproducirlos, modificarlos ni distribuirlos sin nuestra autorización previa y por escrito.\n\n## 7. Enlaces a otros sitios\n\nEl sitio tiene enlaces a WhatsApp, Instagram y Facebook. Esas plataformas tienen sus propios términos y políticas de privacidad, y no somos responsables de su contenido ni de su funcionamiento.\n\n## 8. Responsabilidad\n\nTrabajamos para que el sitio funcione bien y su información esté actualizada, pero no podemos garantizar que esté siempre disponible o libre de errores. No respondemos por daños causados por el uso indebido del sitio, por fallas técnicas ajenas a nosotros o por el contenido de sitios de terceros.\n\n## 9. Datos personales\n\nTratamos los datos que nos compartes según nuestra [Política de tratamiento de datos personales](politica-de-datos.html), nuestro [Aviso de privacidad](aviso-de-privacidad.html) y nuestra [Política de cookies](politica-de-cookies.html).\n\n## 10. Derechos como consumidor\n\nCuando contratas nuestros servicios como consumidor tienes los derechos que reconoce el Estatuto del Consumidor (Ley 1480 de 2011). Para peticiones, quejas o reclamos escríbenos por los canales de contacto. También puedes acudir a la Superintendencia de Industria y Comercio (SIC).\n\n## 11. Cambios a estos términos\n\nPodemos actualizar estos términos. Publicaremos la nueva versión en esta página con su fecha de vigencia.\n\n## 12. Ley aplicable\n\nEstos términos se rigen por las leyes de la República de Colombia. Cualquier controversia se resolverá ante los jueces de Medellín, sin perjuicio de los derechos que tengas como consumidor ante la SIC."}}'::jsonb) on conflict do nothing;

insert into public.servicios (url, orden, publicado, nombre, icono, resumen, titulo, titulo_em, texto, lista_titulo, lista, cta, foto, alt, ocultar, catalogo_titulo, catalogo_titulo_em, catalogo_texto, piezas) values ('construccion', 2, true, 'Construcción', 'i-build', 'Materializamos los diseños con nuestro equipo técnico, procesos definidos y acompañamiento durante toda la obra.', 'De los planos', 'a la realidad.', 'Ejecutamos proyectos de construcción y renovación con una planificación clara, coordinación técnica y un equipo que acompaña cada etapa.', '¿Qué incluye?', '["Diagnóstico técnico.","Coordinación de materiales y personal.","Planimetría.","Ejecución de las actividades de obra.","Seguimiento del cronograma."]'::jsonb, 'Quiero transformar mi espacio', 'torrealta-d01.webp', 'Proyecto de OMBU', '[]'::jsonb, '', '', '', '[]'::jsonb) on conflict do nothing;
insert into public.servicios (url, orden, publicado, nombre, icono, resumen, titulo, titulo_em, texto, lista_titulo, lista, cta, foto, alt, ocultar, catalogo_titulo, catalogo_titulo_em, catalogo_texto, piezas) values ('diseno', 1, true, 'Diseño', 'i-design', 'Convertimos tus ideas en espacios funcionales y personalizados, definiendo cada detalle antes de comenzar.', 'Diseñamos espacios', 'que se sienten tuyos.', 'Transformamos tus ideas en espacios estéticos y funcionales, pensados para tus necesidades y tu comodidad al habitarlos.', '¿Qué incluye?', '["Desarrollo de propuestas de diseño.","Renders.","Planos.","Detalles de carpintería.","Selección de materiales y acabados."]'::jsonb, 'Quiero diseñar mi espacio', 'altos-de-la-concha-d05.webp', 'Proyecto de OMBU', '["construccion"]'::jsonb, '', '', '', '[]'::jsonb) on conflict do nothing;
insert into public.servicios (url, orden, publicado, nombre, icono, resumen, titulo, titulo_em, texto, lista_titulo, lista, cta, foto, alt, ocultar, catalogo_titulo, catalogo_titulo_em, catalogo_texto, piezas) values ('interventoria', 4, true, 'Interventoría', 'i-clipboard', 'Supervisamos proyectos para verificar el cumplimiento técnico, la calidad y los cronogramas establecidos.', 'Supervisión que', 'da tranquilidad.', 'Acompañamos y supervisamos proyectos de construcción para verificar el cumplimiento de criterios técnicos, cronogramas, actividades y estándares de calidad.', 'Espacios que atendemos', '["Viviendas.","Locales comerciales.","Oficinas de gran formato.","Conjuntos residenciales y administraciones."]'::jsonb, 'Solicitar acompañamiento', 'palo-alto-d01.webp', 'Proyecto de OMBU', '[]'::jsonb, '', '', '', '[]'::jsonb) on conflict do nothing;
insert into public.servicios (url, orden, publicado, nombre, icono, resumen, titulo, titulo_em, texto, lista_titulo, lista, cta, foto, alt, ocultar, catalogo_titulo, catalogo_titulo_em, catalogo_texto, piezas) values ('mobiliario', 3, true, 'Mobiliario', 'i-sofa', 'Creamos piezas que complementan tus espacios con identidad, funcionalidad y diseño.', 'Los detalles que', 'completan tu espacio.', 'Complementamos nuestros proyectos con piezas de mobiliario exclusivas y soluciones hechas a la medida que responden a las características de cada ambiente.', 'Lo que ofrecemos', '["Catálogo de 10 a 15 productos exclusivos.","Opciones personalizadas para tu espacio."]'::jsonb, 'Conocer mobiliario', 'aires-del-campestre-d01.webp', 'Proyecto de OMBU', '[]'::jsonb, 'Piezas exclusivas', 'para tu espacio.', 'Entre 10 y 15 productos exclusivos, además de opciones personalizadas. Las fotos y referencias del catálogo están pendientes.', '[{"foto":"","nombre":"Pieza 1 · por confirmar"},{"foto":"","nombre":"Pieza 2 · por confirmar"},{"foto":"","nombre":"Pieza 3 · por confirmar"},{"foto":"","nombre":"Pieza 4 · por confirmar"},{"foto":"","nombre":"Pieza 5 · por confirmar"},{"foto":"","nombre":"Pieza 6 · por confirmar"}]'::jsonb) on conflict do nothing;

insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('aires-del-campestre', 3, true, true, 'Aires del Campestre', '', '', '', 'aires-del-campestre-par-a.webp', 'aires-del-campestre-par-d.webp', '["aires-del-campestre-d01.webp","aires-del-campestre-d02.webp","aires-del-campestre-d03.webp","aires-del-campestre-d04.webp","aires-del-campestre-d05.webp","aires-del-campestre-d06.webp","aires-del-campestre-d07.webp","aires-del-campestre-d08.webp","aires-del-campestre-d09.webp","aires-del-campestre-d10.webp"]'::jsonb, '["aires-del-campestre-a01.webp","aires-del-campestre-a02.webp","aires-del-campestre-a03.webp","aires-del-campestre-a04.webp","aires-del-campestre-a05.webp","aires-del-campestre-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('altos-de-la-concha-2', 9, true, false, 'Altos de la Concha II', '', '', '', 'altos-de-la-concha-2-par-a.webp', 'altos-de-la-concha-2-par-d.webp', '["altos-de-la-concha-2-d01.webp","altos-de-la-concha-2-d02.webp","altos-de-la-concha-2-d03.webp","altos-de-la-concha-2-d04.webp","altos-de-la-concha-2-d05.webp","altos-de-la-concha-2-d06.webp","altos-de-la-concha-2-d07.webp","altos-de-la-concha-2-d08.webp","altos-de-la-concha-2-d09.webp","altos-de-la-concha-2-d10.webp"]'::jsonb, '["altos-de-la-concha-2-a01.webp","altos-de-la-concha-2-a02.webp","altos-de-la-concha-2-a03.webp","altos-de-la-concha-2-a04.webp","altos-de-la-concha-2-a05.webp","altos-de-la-concha-2-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('altos-de-la-concha', 12, true, false, 'Altos de la Concha', '', '', '', 'altos-de-la-concha-par-a.webp', 'altos-de-la-concha-par-d.webp', '["altos-de-la-concha-d01.webp","altos-de-la-concha-d02.webp","altos-de-la-concha-d03.webp","altos-de-la-concha-d04.webp","altos-de-la-concha-d05.webp","altos-de-la-concha-d06.webp","altos-de-la-concha-d07.webp","altos-de-la-concha-d08.webp","altos-de-la-concha-d09.webp","altos-de-la-concha-d10.webp"]'::jsonb, '["altos-de-la-concha-a01.webp","altos-de-la-concha-a02.webp","altos-de-la-concha-a03.webp","altos-de-la-concha-a04.webp","altos-de-la-concha-a05.webp","altos-de-la-concha-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('altos-de-la-rioja', 7, true, false, 'Altos de la Rioja', '', '', '', 'altos-de-la-rioja-par-a.webp', 'altos-de-la-rioja-par-d.webp', '["altos-de-la-rioja-d01.webp","altos-de-la-rioja-d02.webp","altos-de-la-rioja-d03.webp","altos-de-la-rioja-d04.webp","altos-de-la-rioja-d05.webp","altos-de-la-rioja-d06.webp","altos-de-la-rioja-d07.webp","altos-de-la-rioja-d08.webp","altos-de-la-rioja-d09.webp","altos-de-la-rioja-d10.webp"]'::jsonb, '["altos-de-la-rioja-a01.webp","altos-de-la-rioja-a02.webp","altos-de-la-rioja-a03.webp","altos-de-la-rioja-a04.webp","altos-de-la-rioja-a05.webp","altos-de-la-rioja-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('avignon', 13, true, false, 'Avignon', '', '', '', 'avignon-par-a.webp', 'avignon-par-d.webp', '["avignon-d01.webp","avignon-d02.webp","avignon-d03.webp","avignon-d04.webp","avignon-d05.webp","avignon-d06.webp","avignon-d07.webp","avignon-d08.webp","avignon-d09.webp","avignon-d10.webp"]'::jsonb, '["avignon-a01.webp","avignon-a02.webp","avignon-a03.webp","avignon-a04.webp","avignon-a05.webp","avignon-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('baltico', 15, true, false, 'Báltico', '', '', '', '', '', '[]'::jsonb, '[]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('bosque-alto', 6, true, true, 'Bosque Alto', '', '', '', 'bosque-alto-par-a.webp', 'bosque-alto-par-d.webp', '["bosque-alto-d01.webp","bosque-alto-d02.webp","bosque-alto-d03.webp","bosque-alto-d04.webp","bosque-alto-d05.webp","bosque-alto-d06.webp","bosque-alto-d07.webp","bosque-alto-d08.webp"]'::jsonb, '["bosque-alto-a01.webp","bosque-alto-a02.webp","bosque-alto-a03.webp","bosque-alto-a04.webp","bosque-alto-a05.webp","bosque-alto-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('casa-mediterranea', 16, true, false, 'Casa Mediterránea', '', '', '', '', '', '[]'::jsonb, '[]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('fenikas', 2, true, true, 'Fenikas', '', '', '', 'fenikas-par-a.webp', 'fenikas-par-d.webp', '["fenikas-d01.webp","fenikas-d02.webp","fenikas-d03.webp","fenikas-d04.webp","fenikas-d05.webp","fenikas-d06.webp","fenikas-d07.webp","fenikas-d08.webp","fenikas-d09.webp","fenikas-d10.webp"]'::jsonb, '["fenikas-a01.webp","fenikas-a02.webp","fenikas-a03.webp","fenikas-a04.webp","fenikas-a05.webp","fenikas-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('kuna-1002', 5, true, true, 'Kuna 1002', '', '', '', 'kuna-1002-par-a.webp', 'kuna-1002-par-d.webp', '["kuna-1002-d01.webp","kuna-1002-d02.webp","kuna-1002-d03.webp","kuna-1002-d04.webp","kuna-1002-d05.webp","kuna-1002-d06.webp","kuna-1002-d07.webp"]'::jsonb, '["kuna-1002-a01.webp","kuna-1002-a02.webp","kuna-1002-a03.webp","kuna-1002-a04.webp","kuna-1002-a05.webp","kuna-1002-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('kuna-802', 8, true, false, 'Kuna 802', '', '', '', 'kuna-802-par-a.webp', 'kuna-802-par-d.webp', '["kuna-802-d01.webp","kuna-802-d02.webp","kuna-802-d03.webp","kuna-802-d04.webp","kuna-802-d05.webp","kuna-802-d06.webp","kuna-802-d07.webp"]'::jsonb, '["kuna-802-a01.webp","kuna-802-a02.webp","kuna-802-a03.webp","kuna-802-a04.webp","kuna-802-a05.webp","kuna-802-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('palmar-de-la-abadia', 11, true, false, 'Palmar de la Abadía', '', '', '', 'palmar-de-la-abadia-par-a.webp', 'palmar-de-la-abadia-par-d.jpg', '["palmar-de-la-abadia-d01.webp","palmar-de-la-abadia-d02.webp","palmar-de-la-abadia-d03.webp","palmar-de-la-abadia-d04.webp","palmar-de-la-abadia-d05.webp","palmar-de-la-abadia-d06.webp","palmar-de-la-abadia-d07.webp","palmar-de-la-abadia-d08.webp","palmar-de-la-abadia-d09.webp","palmar-de-la-abadia-d10.webp"]'::jsonb, '["palmar-de-la-abadia-a01.webp","palmar-de-la-abadia-a02.webp","palmar-de-la-abadia-a03.webp","palmar-de-la-abadia-a04.webp","palmar-de-la-abadia-a05.webp","palmar-de-la-abadia-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('palo-alto', 4, true, true, 'Palo Alto', '', '', '', 'palo-alto-par-a.webp', 'palo-alto-par-d.webp', '["palo-alto-d01.webp","palo-alto-d02.webp","palo-alto-d03.webp","palo-alto-d04.webp","palo-alto-d05.webp","palo-alto-d06.webp","palo-alto-d07.webp","palo-alto-d08.webp","palo-alto-d09.webp","palo-alto-d10.webp"]'::jsonb, '["palo-alto-a01.webp","palo-alto-a02.webp","palo-alto-a03.webp","palo-alto-a04.webp","palo-alto-a05.webp","palo-alto-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('salento', 18, true, false, 'Salento', '', '', '', '', '', '[]'::jsonb, '[]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('tierra-clara', 14, true, false, 'Tierra Clara', '', '', '', '', '', '[]'::jsonb, '[]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('torrealta', 1, true, true, 'Torrealta', '', '', '', 'torrealta-par-a.webp', 'torrealta-par-d.webp', '["torrealta-d01.webp","torrealta-d02.webp","torrealta-d03.webp","torrealta-d04.webp","torrealta-d05.webp","torrealta-d06.webp","torrealta-d07.webp","torrealta-d08.webp","torrealta-d09.webp","torrealta-d10.webp"]'::jsonb, '["torrealta-a01.webp","torrealta-a02.webp","torrealta-a03.webp","torrealta-a04.webp","torrealta-a05.webp","torrealta-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('torrebalsillas', 10, true, false, 'Torrebalsillas', '', '', '', 'torrebalsillas-par-a.webp', 'torrebalsillas-par-d.webp', '["torrebalsillas-d01.webp","torrebalsillas-d02.webp","torrebalsillas-d03.webp","torrebalsillas-d04.webp","torrebalsillas-d05.webp","torrebalsillas-d06.webp","torrebalsillas-d07.webp","torrebalsillas-d08.webp","torrebalsillas-d09.webp","torrebalsillas-d10.webp"]'::jsonb, '["torrebalsillas-a01.webp","torrebalsillas-a02.webp","torrebalsillas-a03.webp","torrebalsillas-a04.webp","torrebalsillas-a05.webp","torrebalsillas-a06.webp"]'::jsonb) on conflict do nothing;
insert into public.proyectos (url, orden, publicado, destacado, nombre, tipo, servicios, descripcion, foto_antes, foto_despues, despues, antes) values ('twins', 17, true, false, 'Twins', '', '', '', '', '', '[]'::jsonb, '[]'::jsonb) on conflict do nothing;

insert into public.blog (url, publicado, fecha, autor, categoria, lectura, titulo, titulo_em, foto, alt, pie_foto, resumen, cuerpo) values ('cocina-abierta', true, '2026-09-15', 'Equipo OMBU', 'Diseño e interiorismo', 5, 'Cocina abierta:', 'lo que debes saber antes de tumbar un muro', 'comparador-despues.webp', 'Cocina abierta con isla blanca y paneles de madera, renovada por OMBU', 'Cocina renovada por OMBU', 'Integrar la cocina con la sala cambia por completo un apartamento. Antes de derribar, revisa estos cinco puntos.', 'Pocas decisiones transforman tanto un apartamento como abrir la cocina hacia la sala. Gana luz, gana amplitud y la cocina deja de ser un cuarto aparte. Pero antes de tumbar un muro hay que hacer la tarea.

![Antes: comedor cerrado con paredes blancas y piso de baldosa](comparador-antes.webp "Antes")
![Después: cocina abierta con isla blanca y paneles de madera](comparador-despues.webp "Después")

## 1. ¿Ese muro se puede tumbar?

Es lo primero. En muchos edificios los muros hacen parte de la estructura y no se pueden demoler. Un profesional debe revisarlo con los planos del edificio antes de tomar cualquier decisión.

## 2. Olores y ventilación

Con la cocina integrada, el olor viaja a la sala. Una buena campana extractora, bien dimensionada y con salida adecuada, no es un lujo: es parte del diseño.

## 3. Instalaciones

Mover el lavaplatos o la estufa implica mover agua, desagües, gas y electricidad. Se puede, pero hay que planearlo desde el diseño para que no aparezca como sorpresa en la obra.

> Una cocina abierta se diseña para verse bien incluso cuando está en uso.

## 4. Isla, barra y circulación

La isla es la protagonista, pero necesita espacio alrededor para moverse con comodidad y abrir puertas y cajones. Si el espacio no da, una barra contra la pared cumple la misma función.

## 5. Materiales que resistan

La cocina queda a la vista todo el tiempo. Superficies fáciles de limpiar, muebles a la medida que escondan los electrodomésticos y una iluminación por capas hacen que se vea ordenada incluso en plena preparación.

¿Estás pensando en abrir tu cocina? Cuéntanos cómo es tu espacio y lo revisamos contigo.') on conflict do nothing;
insert into public.blog (url, publicado, fecha, autor, categoria, lectura, titulo, titulo_em, foto, alt, pie_foto, resumen, cuerpo) values ('ideas-espacios-amplios', true, '2026-09-08', 'Equipo OMBU', 'Inspiración y tendencias', 4, '5 ideas para que tu apartamento', 'se vea más amplio', 'avignon-d01.webp', 'Sala del proyecto Avignon, renovado por OMBU', 'Proyecto Avignon · OMBU', 'Color, luz, muebles a la medida y espacios integrados: así se gana amplitud sin sumar un solo metro.', 'No siempre hace falta más metros para sentir más espacio. Estas cinco decisiones, que aplicamos una y otra vez en nuestros proyectos, cambian por completo la percepción de un apartamento.

## 1. Una paleta clara y continua

Muros y techos claros reflejan la luz y borran los límites. Si además los tonos se repiten de un espacio a otro, el ojo recorre el apartamento sin cortes.

![Sala amplia con piso de madera y muros claros](avignon-d02.webp "Proyecto Avignon · OMBU")

## 2. El mismo piso en todo el apartamento

Cambiar de material en cada espacio parte visualmente el apartamento. Un solo piso, continuo, hace que todo se lea como un gran ambiente.

## 3. Almacenamiento a la medida

El desorden achica cualquier espacio. Clósets y muebles empotrados, del piso al techo, guardan mucho más y desaparecen visualmente.

![Mueble empotrado en madera clara](altos-de-la-concha-2-d05.webp "Proyecto Altos de la Concha II · OMBU")

## 4. Luz, natural y artificial

Despeja las ventanas y combina luz general con luz indirecta: rieles, tiras LED en muebles y lámparas puntuales. Un espacio bien iluminado siempre se ve más grande.

![Sala con ventanales amplios e iluminación en rieles](torrealta-d06.webp "Proyecto Torrealta · OMBU")

## 5. Integrar espacios

Abrir la cocina hacia el comedor o la sala une dos ambientes en uno y multiplica la sensación de amplitud. Eso sí: antes hay que revisar qué muros se pueden intervenir.

![Cocina integrada con isla y comedor](torrebalsillas-par-d.webp "Proyecto Torrebalsillas · OMBU")

¿Quieres ver cómo se vería tu apartamento? Escríbenos y lo pensamos juntos.') on conflict do nothing;
insert into public.blog (url, publicado, fecha, autor, categoria, lectura, titulo, titulo_em, foto, alt, pie_foto, resumen, cuerpo) values ('preguntas-antes-de-contratar', true, '2026-09-22', 'Equipo OMBU', 'Consejos para renovar', 5, '7 preguntas que debes hacer', 'antes de contratar una remodelación', 'torrealta-d01.webp', 'Espacio social del proyecto Torrealta, renovado por OMBU', 'Proyecto Torrealta · OMBU', 'Pólizas, contrato, quién dirige la obra y cómo se paga. Lo que tienes que saber antes de firmar.', 'Elegir quién va a renovar tu espacio es la decisión más importante de todo el proyecto. Estas siete preguntas te ayudan a comparar propuestas con la cabeza fría.

## 1. ¿Trabajan con pólizas y contrato por escrito?

Es la primera pregunta y no es negociable. Un contrato claro define alcance, tiempos y valores; las pólizas te protegen si algo no se cumple.

## 2. ¿Quién dirige la obra?

Pregunta si habrá un arquitecto o un profesional a cargo, y si será tu contacto directo. Saber a quién llamar hace toda la diferencia.

## 3. ¿Puedo ver proyectos terminados?

Las fotos de antes y después dicen más que cualquier promesa. Pide ver obras similares a la tuya y, si puedes, habla con clientes anteriores.

## 4. ¿Qué incluye exactamente el presupuesto?

Materiales, mano de obra, diseño, retiro de escombros, limpieza final. Un presupuesto barato que deja por fuera la mitad termina siendo el más caro.

> La mejor propuesta no es la más barata: es la que no te deja sorpresas.

## 5. ¿Cuál es el cronograma?

Pide fechas por etapa y pregunta cómo te avisarán si algo se retrasa. Un buen equipo comunica antes de que tú tengas que preguntar.

## 6. ¿Cómo son los pagos?

Lo sano es pagar por avance: un anticipo razonable y el resto a medida que la obra se ejecuta. Desconfía de quien pide el total por adelantado.

## 7. ¿Qué garantía tienen los trabajos?

Pregunta qué cubre la garantía, por cuánto tiempo y cómo se solicita. Un equipo que confía en su trabajo lo explica sin rodeos.

Si quieres, hazle estas mismas preguntas a OMBU. Escríbenos y te respondemos una por una.') on conflict do nothing;
insert into public.blog (url, publicado, fecha, autor, categoria, lectura, titulo, titulo_em, foto, alt, pie_foto, resumen, cuerpo) values ('remodelar-apartamento-medellin', true, '2026-09-29', 'Equipo OMBU', 'Consejos para renovar', 6, 'Cómo remodelar tu apartamento en Medellín sin estrés:', 'guía paso a paso', 'aires-del-campestre-d01.webp', 'Sala y comedor del proyecto Aires del Campestre, renovado por OMBU', 'Proyecto Aires del Campestre · OMBU', 'Del primer boceto a la entrega de llaves: los siete pasos que evitan sobrecostos, retrasos y dolores de cabeza.', 'Renovar un apartamento es una de las mejores inversiones que puedes hacer en tu patrimonio. También es una de las que más miedo da: sobrecostos, obras que no terminan, decisiones que se toman a última hora. La buena noticia es que casi todo eso se evita con un proceso claro.

## 1. Define qué quieres, y para qué

Antes de hablar de materiales, piensa en cómo vives. ¿Cocinas todos los días o casi nunca? ¿Trabajas desde casa? ¿Necesitas más almacenamiento o más luz? Haz una lista de los espacios que quieres transformar y ordénala por prioridad.

Guarda fotos de referencia de lo que te gusta y, sobre todo, de lo que no. Esa carpeta le ahorra horas a cualquier arquitecto.

## 2. Fija un presupuesto con margen

Un presupuesto realista incluye diseño, materiales, mano de obra y un colchón para imprevistos. En remodelaciones es habitual reservar entre un 10 y un 15 % adicional: al abrir un muro o levantar un piso pueden aparecer tuberías o instalaciones que hay que actualizar.

> Cambiar una decisión en el plano cuesta minutos. Cambiarla en plena obra cuesta días.

## 3. Diseña antes de construir

Planos, distribución, acabados y muebles definidos desde el principio. Es la etapa donde más se ahorra, porque cada cambio todavía es gratis. Pide ver el diseño completo, con materiales y colores, antes de que empiece la obra.

## 4. Revisa el reglamento de tu edificio

En propiedad horizontal hay reglas: horarios de obra, ingreso de materiales, manejo de escombros y, a veces, permisos de la administración. Conocerlas desde el inicio evita que la obra se detenga por un trámite.

## 5. Contrata con respaldo

Contrato por escrito, cronograma, pólizas y pagos atados al avance real. Si algo sale mal, esas cuatro cosas son tu tranquilidad. En OMBU cada proyecto se trabaja con pólizas y formalidad, porque renovar es cuidar tu patrimonio.

## 6. Un solo responsable durante la obra

Cuando cada oficio responde por su lado, los problemas caen en el cliente. Lo ideal es tener un arquitecto que coordine a todo el equipo y te mantenga al tanto del avance, sin que tengas que estar en la obra todos los días.

## 7. Recibe punto por punto

Al final, recorre cada espacio con una lista: acabados, puertas, grifería, iluminación, limpieza. Lo que quede pendiente se anota y se programa. Y pregunta por las garantías de cada trabajo.

¿Tienes un espacio en mente? Cuéntanos qué quieres transformar y te asesoramos de manera personalizada.') on conflict do nothing;

-- Editores del panel
insert into public.editores (email, nombre) values ('ombumercadeo@gmail.com', 'OMBU') on conflict do nothing;
