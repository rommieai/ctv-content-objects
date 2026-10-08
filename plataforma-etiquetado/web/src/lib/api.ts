export interface Usuario { id: number; usuario: string; nombre: string; rol: "admin" | "revisor" }
export interface Iab { codigo: string; es: string; en: string; tax: string }
export interface Unidad { valor: string; agregado: boolean; estrato: string }
export interface Campo {
  campo: string; nombre: string; valor: string; llenado: boolean; corregido?: boolean; original: string; riesgo: string;
  unidades: Unidad[]; significado: { iab: Iab[] } | { texto: string } | null;
}
export interface Etiqueta { veredicto: string; correcto: string; ts: string }
export interface Registro {
  fila_id: number; muestra_id: number | null; titulo: string; app: string; bundle: string; publisher: string;
  pais: string; requests: number; campos: Campo[]; extra: any;
  ayuda: { busqueda: string; imdb: string; imdb_texto: string };
  etiquetas: Record<string, Etiqueta>; nota: string; crudo?: Record<string, any>;
}
export interface Opciones {
  version: string; fuente: string; total_filas: number; filas_llenadas: number; tarjetas_muestra: number;
  campos: { campo: string; nombre: string }[]; estratos: string[]; paises: string[];
}
export type Ambito = "muestra" | "completo";

export class ErrorApi extends Error { constructor(public estado: number, msg: string) { super(msg); } }

export async function api<T = any>(ruta: string, opts: { metodo?: string; cuerpo?: unknown } = {}): Promise<T> {
  const r = await fetch(ruta, {
    method: opts.metodo ?? "GET", credentials: "same-origin",
    headers: opts.cuerpo !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: opts.cuerpo !== undefined ? JSON.stringify(opts.cuerpo) : undefined,
  });
  const datos = await r.json().catch(() => ({}));
  if (!r.ok) throw new ErrorApi(r.status, datos.error ?? `Error ${r.status}`);
  return datos as T;
}

export const fmt = (n: number) => (n ?? 0).toLocaleString("es-MX");
export const pct = (x: number | null) => x === null || x === undefined ? "—" : `${Math.round(100 * x)}%`;
export const llavesUnidades = (r: Registro) =>
  r.campos.filter(c => c.llenado).flatMap(c => c.unidades.map(u => `${c.campo}|${u.valor}`));
export const pendientesDe = (r: Registro) => llavesUnidades(r).filter(k => !r.etiquetas[k]?.veredicto).length;

const METODO: Record<string, string> = {
  corregido_imdb: "corregido con IMDb (venía del vendedor)", corregido_genero: "corregido con el género de la fila (venía del vendedor)",
  intra_titulo: "copiado de otra ruta del mismo título", derivado_genero: "derivado del género",
  derivado_tipo: "tipo película/serie de IMDb", imdb: "IMDb", wikidata: "Wikidata", tvmaze: "TVmaze",
  app_semantica: "semántica de la app", genero_declarado: "género declarado por el vendedor",
};
const CAMPO: Record<string, string> = {
  contentGenre: "Género", contentCategory: "Categoría", contentSeries: "Serie", contentRating: "Clasificación",
  contentIsLiveStream: "En vivo", contentLength: "Duración", contentLanguage: "Idioma",
  contentCategory_afinado: "Categoría (código específico)", _ficha_externa: "Ficha IMDb = misma obra",
};
export const nombreCampo = (c: string) => CAMPO[c] ?? c;
export function nombreEstrato(e: string) {
  const [c, m] = e.split("|");
  if (c === "_original") return `${CAMPO[m] ?? m} · valor del vendedor marcado mal`;
  if (c === "_previo") return `${CAMPO[m] ?? m} · lo correcto era lo que venía antes`;
  return m ? `${CAMPO[c] ?? c} · ${METODO[m] ?? m}` : CAMPO[c] ?? c;
}
