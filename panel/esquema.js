// Estructura editable de cada página: secciones y campos, en el mismo orden en que se ven en el sitio.
// La usa el panel /admin para armar los formularios. Los archivos de contenido/paginas/ tienen estas mismas claves.
// Tipos de campo: texto, largo, numero, fecha, bool, foto, lista, grupo, servicios, opciones.

const T = (label, name, o = {}) => ({ tipo: 'texto', label, name, ...o });
const L = (label, name, o = {}) => ({ tipo: 'largo', label, name, ...o });
const F = (label = 'Foto', name = 'foto') => ({ tipo: 'foto', label, name });

const FORMATO = 'Dentro del texto: **negrita**, *cursiva*, [texto del enlace](https://…) y {pendiente} (sale resaltado).';

// Encabezado de una sección: etiqueta pequeña + titular + segunda línea en cursiva
const cabeza = (conEyebrow = true) => [
  ...(conEyebrow ? [T('Etiqueta pequeña', 'eyebrow')] : []),
  T('Titular (parte en negrita)', 'titulo'),
  T('Titular (parte en cursiva)', 'titulo_em'),
];
const seo = {
  id: 'seo', nombre: 'Google y redes sociales',
  campos: [T('Título para Google', 'titulo', { max: 60 }), L('Descripción para Google', 'descripcion', { max: 155 })],
};
const parrafos = { tipo: 'lista', name: 'parrafos', label: 'Párrafos', nuevo: '', item: L('', ''), ayuda: FORMATO };
const documento = nombre => ({
  id: 'documento', nombre,
  campos: [
    ...cabeza(false), L('Introducción', 'texto'), T('Vigente desde', 'vigencia', { ayuda: 'Ej.: 3 de noviembre de 2026' }),
    L('Texto del documento', 'cuerpo', {
      filas: 24,
      ayuda: `## Subtítulo · - lista · ${FORMATO} [[responsable]] pone los datos legales de «Datos generales» y [[cookies]] el botón de preferencias.`,
    }),
  ],
});

export const PAGINAS = [
  {
    id: 'general', nombre: 'Datos generales', ruta: null,
    resumen: 'Contacto, datos legales y lo que se repite en varias páginas',
    secciones: [
      { id: 'contacto', nombre: 'Canales de contacto', campos: [
        T('WhatsApp', 'whatsapp', { ayuda: 'Con indicativo: +57 310 599 6809. Cambia todos los botones de WhatsApp del sitio.' }),
        T('Mensaje inicial de WhatsApp', 'mensaje_whatsapp'),
        T('Enlace de Instagram', 'instagram_url'), T('Usuario de Instagram', 'instagram_txt'),
        T('Enlace de Facebook', 'facebook_url'), T('Ubicación', 'ubicacion'),
      ] },
      { id: 'legal', nombre: 'Datos legales', ayuda: 'Salen en los documentos legales. Si un campo está vacío, el sitio muestra «por confirmar».', campos: [
        T('Responsable (razón social)', 'responsable'), T('NIT', 'nit'), T('Dirección', 'direccion'), T('Correo', 'correo'),
      ] },
      { id: 'pie', nombre: 'Pie de página', campos: [
        T('Frase (parte normal)', 'frase'), T('Frase (parte en cursiva)', 'frase_em'), T('Texto de derechos', 'derechos'),
      ] },
      { id: 'banda', nombre: 'Banda final', ayuda: 'La franja con foto que cierra casi todas las páginas.', campos: [
        ...cabeza(false), L('Texto', 'texto'), T('Botón', 'boton'), F('Foto de fondo'),
      ] },
      { id: 'atributos', nombre: '¿Por qué elegir OMBU? (atributos)', ayuda: 'Salen en Inicio y en Nosotros.', campos: [
        { tipo: 'lista', name: 'lista', label: 'Atributos', nuevo: { titulo: '', texto: '' }, campos: [T('Título', 'titulo'), L('Texto', 'texto')] },
      ] },
      { id: 'pasos', nombre: 'Cómo trabajamos (4 pasos)', ayuda: 'Salen en Inicio y en Servicios.', campos: [
        { tipo: 'lista', name: 'lista', label: 'Pasos', nuevo: { titulo: '', texto: '' }, campos: [T('Título', 'titulo'), L('Texto', 'texto')] },
      ] },
      { id: 'testimonios', nombre: 'Testimonios', campos: [
        ...cabeza(),
        { tipo: 'lista', name: 'lista', label: 'Testimonios', nuevo: { nombre: '', detalle: '', cita: '', texto: '' },
          campos: [T('Nombre', 'nombre'), T('Detalle', 'detalle', { ayuda: 'Ej.: Renovación total de apartamento' }), L('Frase destacada', 'cita'), L('Texto', 'texto')] },
      ] },
      { id: 'faq', nombre: 'Preguntas frecuentes', ayuda: 'Salen en Inicio, Servicios y Contacto.', campos: [
        ...cabeza(),
        { tipo: 'lista', name: 'lista', label: 'Preguntas', nuevo: { pregunta: '', respuesta: '' }, campos: [T('Pregunta', 'pregunta'), L('Respuesta', 'respuesta')] },
      ] },
    ],
  },
  {
    id: 'inicio', nombre: 'Inicio', ruta: '',
    secciones: [
      { id: 'portada', nombre: 'Portada', campos: [
        ...cabeza(), L('Texto de apoyo', 'texto'), T('Botón principal', 'boton'), T('Botón secundario', 'boton2'),
        { tipo: 'lista', name: 'garantias', label: 'Garantías', nuevo: '', item: T('', '') },
        F('Foto de portada'), T('Descripción de la foto', 'alt', { ayuda: 'Para Google y lectores de pantalla.' }),
      ] },
      { id: 'sobre', nombre: 'Sobre OMBU', campos: [...cabeza(), parrafos, T('Botón', 'boton'), F(), T('Descripción de la foto', 'alt')] },
      { id: 'servicios', nombre: 'Nuestros servicios', ayuda: 'Las tarjetas se editan en la sección «Servicios» del menú.', campos: [...cabeza(), T('Botón', 'boton')] },
      { id: 'proceso', nombre: 'Cómo trabajamos', ayuda: 'Los 4 pasos se editan en «Datos generales».', campos: [...cabeza(), L('Texto', 'texto'), T('Botón', 'boton')] },
      { id: 'proyectos', nombre: 'Proyectos destacados', ayuda: 'Los proyectos que salen aquí se marcan con «Destacado» en la sección «Proyectos».', campos: [
        ...cabeza(), L('Texto', 'texto'), T('Cifra', 'cifra', { ayuda: 'Ej.: +80' }), T('Texto de la cifra', 'cifra_txt'), T('Botón', 'boton'),
      ] },
      { id: 'por_que', nombre: '¿Por qué elegir OMBU?', ayuda: 'Los atributos se editan en «Datos generales».', campos: cabeza() },
      { id: 'blog', nombre: 'Blog', campos: [...cabeza(), T('Enlace', 'enlace')] },
      seo,
    ],
  },
  {
    id: 'nosotros', nombre: 'Nosotros', ruta: 'nosotros.html',
    secciones: [
      { id: 'portada', nombre: 'Portada', campos: [...cabeza(false), L('Texto', 'texto')] },
      { id: 'quienes', nombre: 'Quiénes somos', campos: [...cabeza(), parrafos, F(), T('Descripción de la foto', 'alt')] },
      { id: 'diferencia', nombre: 'Lo que nos diferencia', ayuda: 'Los atributos se editan en «Datos generales».', campos: cabeza() },
      { id: 'proceso', nombre: 'Cómo trabajamos', campos: [
        ...cabeza(), L('Texto', 'texto'),
        { tipo: 'lista', name: 'etapas', label: 'Etapas', nuevo: { titulo: '', pasos: [] }, campos: [
          T('Nombre de la etapa', 'titulo'),
          { tipo: 'lista', name: 'pasos', label: 'Pasos', nuevo: '', item: L('', '') },
        ] },
      ] },
      { id: 'equipo', nombre: 'Nuestro equipo', campos: [
        ...cabeza(), L('Texto', 'texto'),
        { tipo: 'lista', name: 'fotos', label: 'Fotos', nuevo: { foto: '', texto: '' }, campos: [F(), T('Texto', 'texto')] },
      ] },
      { id: 'cta', nombre: 'Banda final', campos: [T('Botón', 'boton')] },
      seo,
    ],
  },
  {
    id: 'servicios', nombre: 'Servicios (página general)', ruta: 'servicios/index.html',
    secciones: [
      { id: 'portada', nombre: 'Portada', campos: [...cabeza(false), L('Texto', 'texto')] },
      { id: 'lista', nombre: 'Lista de servicios', campos: cabeza() },
      { id: 'otros', nombre: '«Otros servicios» en cada servicio', campos: cabeza() },
      seo,
    ],
  },
  {
    id: 'proyectos', nombre: 'Proyectos (página general)', ruta: 'proyectos.html',
    secciones: [
      { id: 'portada', nombre: 'Portada', campos: [...cabeza(false), L('Texto', 'texto'), T('Cifra', 'cifra'), T('Texto de la cifra', 'cifra_txt')] },
      { id: 'cta', nombre: 'Banda final', campos: [T('Botón', 'boton')] },
      seo,
    ],
  },
  {
    id: 'contacto', nombre: 'Contacto', ruta: 'contacto.html',
    secciones: [
      { id: 'portada', nombre: 'Portada', campos: [...cabeza(false), L('Texto', 'texto')] },
      { id: 'formulario', nombre: 'Formulario', campos: [
        T('Título', 'titulo'), T('Ayuda', 'ayuda'), T('Pregunta del espacio', 'pregunta_espacio'),
        { tipo: 'lista', name: 'opciones', label: 'Opciones de espacio', nuevo: '', item: T('', '') },
        T('Etiqueta de la idea', 'idea'), T('Ejemplo de la idea', 'idea_ejemplo'), T('Botón', 'boton'), T('Nota bajo el botón', 'nota'),
        T('Mensaje de gracias (título)', 'gracias_titulo'), L('Mensaje de gracias (texto)', 'gracias_texto'),
      ] },
      seo,
    ],
  },
  {
    id: 'blog', nombre: 'Blog (página general)', ruta: 'blog/index.html',
    secciones: [{ id: 'portada', nombre: 'Portada', campos: [...cabeza(false), L('Texto', 'texto')] }, seo],
  },
  { id: 'terminos-y-condiciones', nombre: 'Términos y condiciones', ruta: 'legal/terminos-y-condiciones.html', secciones: [documento('Documento')] },
  { id: 'politica-de-datos', nombre: 'Política de datos', ruta: 'legal/politica-de-datos.html', secciones: [documento('Documento')] },
  { id: 'aviso-de-privacidad', nombre: 'Aviso de privacidad', ruta: 'legal/aviso-de-privacidad.html', secciones: [documento('Documento')] },
  { id: 'politica-de-cookies', nombre: 'Política de cookies', ruta: 'legal/politica-de-cookies.html', secciones: [documento('Documento')] },
];
