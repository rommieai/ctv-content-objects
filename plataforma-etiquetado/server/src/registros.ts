// Una fila del consolidado relleno -> registro de revisión (tarjeta): sus content objects, cuáles se
// llenaron de más y en qué unidades se juzgan. Misma lógica que scripts/generar_muestra_revision.py,
// así las etiquetas de la muestra y las del consolidado completo usan las mismas llaves.
import { significado, significadoCategoria, TIPO_ES, type Significado } from "./significados.js";

export const CAMPOS = ["contentGenre", "contentCategory", "contentSeries", "contentRating", "contentIsLiveStream",
  "contentLength", "contentLanguage"] as const;
export const NOMBRE_CAMPO: Record<string, string> = {
  contentGenre: "Género", contentCategory: "Categoría (IAB)", contentSeries: "Serie",
  contentRating: "Clasificación por edad", contentIsLiveStream: "En vivo / lineal",
  contentLength: "Duración (código)", contentLanguage: "Idioma",
};
const EXTERNO = new Set(["imdb", "wikidata", "tvmaze", "derivado_tipo", "corregido_imdb"]);
const SENT = new Set(["not available", "not applicable", "unknown", "n/a", "null", "undefined", "none", "-", ""]);
const MD5_VACIO = "d41d8cd98f00b204e9800998ecf8427e";
export const FICHA = "_ficha_externa";
// Banderas fuera de la cuenta de precisión (su campo empieza con "_", igual que la ficha):
//   _original:<campo>  el valor que mandó el vendedor (no lo llenamos nosotros) está mal
//   _previo:<campo>    llenamos/cambiamos el campo y lo correcto era lo que venía antes
export const ORIGINAL = "_original:";
export const PREVIO = "_previo:";

export type Fila = Record<string, any>;
export interface Unidad { valor: string; agregado: boolean; estrato: string }
export interface Campo {
  campo: string; nombre: string; valor: string; llenado: boolean; corregido: boolean; original: string;
  riesgo: string; unidades: Unidad[]; significado: Significado;
}
export interface Registro {
  fila_id: number; muestra_id: number | null; titulo: string; app: string; bundle: string; publisher: string;
  pais: string; requests: number; campos: Campo[]; extra: any; ayuda: { busqueda: string; imdb: string; imdb_texto: string };
}

/** Una celda cuenta como vacía aunque traiga texto si es un centinela ("Not Available"...). */
export function esUtil(col: string, v: string | null | undefined): boolean {
  const s = (v ?? "").trim();
  if (SENT.has(s.toLowerCase())) return false;
  if (col === "contentSeries" && s === MD5_VACIO) return false;
  if (col === "contentCategory" && ["[-7]", "[]", "[-1]"].includes(s)) return false;
  if (s.includes("{{") || s.includes("}}")) return false;
  return true;
}

// urllib.parse.unquote: decodifica %XX como UTF-8 y reemplaza lo inválido por U+FFFD
const unquote = (s: string) => s.replace(/(%[0-9A-Fa-f]{2})+/g, m => Buffer.from(m.replace(/%/g, ""), "hex").toString("utf8"));

export function tituloLegible(contentTitle: string): string {
  let t = esUtil("contentTitle", contentTitle) ? contentTitle.trim() : "";
  if (t.includes("%")) t = unquote(t);
  if (t.includes("+") && !t.includes(" ")) t = t.replaceAll("+", " ");
  return t;
}

export function construirCampos(f: Fila): Campo[] {
  const af: string = f.contentCategory_afinado_origen ?? "";
  return CAMPOS.map(c => {
    const o: string = f[c + "_origen"] ?? "";
    const lleno = !!o && o !== "original";
    const valor: string = lleno ? (f[c + "_relleno"] ?? "") : (esUtil(c, f[c]) ? String(f[c]).trim() : "");
    const sig = significado(c, valor, f.ext_runtime_min ?? "");
    const unidades: Unidad[] = [];
    if (lleno) {
      const est = `${c}|${o}`;
      if (c === "contentCategory") {
        for (const x of significadoCategoria(valor)) {
          const agregado = !!af && !["IAB1", "IAB1-5", "IAB1-7", "IAB1-22"].includes(x.codigo);
          unidades.push({ valor: x.codigo, agregado, estrato: agregado ? `contentCategory_afinado|${af}` : est });
        }
      } else if (c === "contentGenre") {
        for (const g of valor.split(",").map(x => x.trim()).filter(Boolean)) unidades.push({ valor: g, agregado: false, estrato: est });
      } else {
        unidades.push({ valor, agregado: false, estrato: est });
      }
    }
    return {
      campo: c, nombre: NOMBRE_CAMPO[c], valor, llenado: lleno, corregido: o.startsWith("corregido"), original: String(f[c] ?? "").trim(),
      riesgo: "", unidades, significado: sig,
    };
  });
}

export function usaExterno(f: Fila): boolean {
  return CAMPOS.some(c => EXTERNO.has(f[c + "_origen"])) || ["imdb", "wikidata"].includes(f.contentCategory_afinado_origen);
}

/** Llaves "campo|valor" de los valores llenados (lo que se juzga), sin la pregunta de la ficha. */
export function llaves(campos: Campo[]): string[] {
  return campos.filter(c => c.llenado).flatMap(c => c.unidades.map(u => `${c.campo}|${u.valor}`));
}

const quotePlus = (s: string) => encodeURIComponent(s).replace(/%20/g, "+");

/** Registro de una fila fuera de la muestra (sin caché de IMDb/Wikidata: solo lo que trae el CSV). */
export function construirRegistro(f: Fila): Registro {
  const campos = construirCampos(f);
  const imdb = usaExterno(f) && f.ext_imdb_id ? String(f.ext_imdb_id) : "";
  const tipo = TIPO_ES[f.ext_tipo] ?? f.ext_tipo ?? "";
  return {
    fila_id: f.id, muestra_id: f.muestra_id ?? null, titulo: f.titulo, app: f.app_name, bundle: f.page_url,
    publisher: f.publisher, pais: f.country, requests: f.total_requests, campos,
    extra: imdb ? {
      imdb_id: imdb, tipo, anio_inicio: f.ext_anio ?? "", duracion_min: f.ext_runtime_min ?? "",
      confianza: f.ext_confianza ?? "", ligero: true,
    } : null,
    ayuda: {
      busqueda: `https://www.google.com/search?q=${quotePlus(`"${f.titulo}" ${f.app_name}`)}`,
      imdb: imdb ? `https://www.imdb.com/title/${imdb}/` : "",
      imdb_texto: imdb ? `${imdb} (${[tipo, f.ext_anio].filter(Boolean).join(", ")})` : "",
    },
  };
}
