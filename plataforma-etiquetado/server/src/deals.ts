// Armador de deals: compara, sobre el corte vigente, lo que alcanzarían los filtros nativos de PubMatic
// con lo que alcanza la recomendación armada con la base enriquecida (lista de títulos), y crea en
// PubMatic el deal recomendado (siempre en pausa).
//
// Los datos vienen de deals.db, que genera scripts/exportar_deals_db.py en cada tanda (mismos criterios
// que scripts/compilar_deal.py y scripts/simular_deals.py). Lo único que se guarda aquí son los trabajos
// de creación, en la base de la plataforma.
import { existsSync, statSync } from "node:fs";
import Database from "better-sqlite3";
import type { Hono } from "hono";
import { significadoCategoria } from "./significados.js";
import { aiConfigurado, ErrorAi, interpretarBrief, type Catalogo, type PlanBrief } from "./ai.js";
import { DSPS } from "./dsps.js";
import { crearDeal, DealSinPausar, PUBMATIC, pubmaticConfigurado, type Condiciones, type SenalRegla } from "./pubmatic.js";

const RUTA = process.env.DEALS_DB ?? "/data/deals.db";
const MAX_VALORES = 10_000;       // valores por deal en la carga por CSV de PubMatic
const MAX_BYTES = 500 * 1000;     // tamaño máximo del CSV
const MAX_SENALES = 3;            // señales que PubMatic admite en una misma regla de contenido
const RE_NOMBRE = /^[A-Za-z0-9][A-Za-z0-9 ._-]{2,99}$/;

// Señales de contenido que PubMatic deja filtrar al armar el deal pero que el reporte no trae: no se puede medir
// cuánto inventario tienen, así que no cambian los números de la comparación; solo viajan al deal, en una segunda
// regla. `opciones` son los valores de OpenRTB cuando la señal es un código; sin opciones es texto libre.
const SENALES_PUBMATIC = [
  { nombre: "Channel", es: "Canal", ayuda: "Canal en el que va el contenido" },
  { nombre: "Network", es: "Cadena / network", ayuda: "Cadena a la que pertenece el canal" },
  { nombre: "Season", es: "Temporada", ayuda: "Ej. Season 3" },
  { nombre: "Episode", es: "Episodio", ayuda: "Número de episodio" },
  { nombre: "Keywords", es: "Palabras clave", ayuda: "Palabras clave que describen el contenido" },
  { nombre: "Producer Name", es: "Productora", ayuda: "Ej. Warner Bros" },
  { nombre: "Producer Domain", es: "Dominio de la productora", ayuda: "Ej. warnerbros.com" },
  { nombre: "ID", es: "ID del contenido", ayuda: "Identificador único del contenido" },
  { nombre: "User Rating", es: "Calificación de usuarios", ayuda: "Número de likes, estrellas, etc." },
  { nombre: "Production Quality", es: "Calidad de producción", ayuda: "", opciones: [["1", "Profesional"], ["2", "Semiprofesional (prosumer)"], ["3", "Generado por usuarios (UGC)"], ["0", "Desconocida"]] },
  { nombre: "Context", es: "Tipo de contenido", ayuda: "", opciones: [["1", "Video"], ["2", "Juego"], ["3", "Música"], ["4", "Aplicación"], ["5", "Texto"], ["6", "Otro"], ["7", "Desconocido"]] },
  { nombre: "QA Media Rating", es: "Clasificación IQG", ayuda: "", opciones: [["1", "Todo público"], ["2", "Mayores de 12"], ["3", "Adultos"]] },
  { nombre: "Source Relationship", es: "Relación con la fuente", ayuda: "", opciones: [["1", "Directa"], ["0", "Indirecta"]] },
  { nombre: "Embeddable", es: "Se puede incrustar", ayuda: "", opciones: [["1", "Sí"], ["0", "No"]] },
] as { nombre: string; es: string; ayuda: string; opciones?: [string, string][] }[];
const OPERADORES = ["is", "contains", "is any"] as const;
export interface SenalExtra { senal: string; operador: typeof OPERADORES[number]; valores: string[] }

/** Señales solo-PubMatic pedidas desde la web: [{ senal, operador, valores }]. */
function leerExtras(x: unknown): SenalExtra[] | string {
  if (x === undefined || x === null) return [];
  if (!Array.isArray(x) || x.length > SENALES_PUBMATIC.length) return "Señales de PubMatic inválidas";
  const out: SenalExtra[] = [];
  for (const e of x) {
    const def = SENALES_PUBMATIC.find(s => s.nombre === String(e?.senal ?? ""));
    if (!def) return "Señal de PubMatic desconocida";
    if (out.some(o => o.senal === def.nombre)) return `La señal ${def.es} está repetida`;
    const operador = String(e?.operador ?? "is") as SenalExtra["operador"];
    if (!OPERADORES.includes(operador) || (def.opciones && operador === "contains")) return `Operador inválido en ${def.es}`;
    const crudos: string[] = (Array.isArray(e?.valores) ? e.valores : String(e?.valores ?? "").split(/[,\n]/)).map((v: unknown) => String(v).trim());
    const valores = [...new Set(crudos.filter(Boolean))];
    if (operador === "is any") { out.push({ senal: def.nombre, operador, valores: [] }); continue; }
    if (!valores.length) return `Falta el valor de ${def.es}`;
    if (valores.length > 200 || valores.some(v => v.length > 120)) return `Demasiados valores (o muy largos) en ${def.es}`;
    if (def.opciones && valores.some(v => !def.opciones!.some(([cod]) => cod === v))) return `Valor inválido en ${def.es}`;
    out.push({ senal: def.nombre, operador, valores });
  }
  return out;
}

type Db = InstanceType<typeof Database>;
interface Tot { filas: number; req: number; vend: number; gasto: number }

// Content objects del reporte por los que se puede filtrar. `col` es la columna de `base` con lo que declara el
// publisher (formato ';valor;'). Los enriquecibles tienen además lista de títulos en titulo_attr: en la
// recomendación entran por título aunque el publisher no los declare. Idioma y «trae título» solo valen como
// vienen (el idioma nunca se rellena), así que filtran igual en los dos caminos.
// La categoría tiene dos filtros sobre el mismo dato (`dato` = el tipo en valores y titulo_attr): los códigos
// IAB 1.0 («IAB1-5») y los numéricos de IAB 2.2 / 3.0 («333»). Son taxonomías distintas y no se cruzan.
const ATRIBUTOS = [
  { tipo: "genero", col: "gen_decl", enriquecible: true },
  { tipo: "categoria", col: "cat_decl", enriquecible: true, formato: /^IAB\d/ },
  { tipo: "categoria_num", col: "cat_decl", enriquecible: true, dato: "categoria", formato: /^\d+$/ },
  { tipo: "serie", col: "ser_decl", enriquecible: true },
  { tipo: "rating", col: "rat_decl", enriquecible: true },
  { tipo: "duracion", col: "len_decl", enriquecible: true },
  { tipo: "envivo", col: "live_decl", enriquecible: true },
  { tipo: "idioma", col: "lang_decl", enriquecible: false },
  { tipo: "con_titulo", col: "tit_decl", enriquecible: false },
] as const;
type Tipo = typeof ATRIBUTOS[number]["tipo"];
type Filtro = { paises: string[]; titulo: string; extras: SenalExtra[] } & Record<Tipo, string>;
const escaparLike = (v: string) => v.replace(/[\\%_]/g, "\\$&");
const datoDe = (a: typeof ATRIBUTOS[number]) => ("dato" in a ? a.dato : a.tipo);

// La base de datos se reemplaza en cada tanda: se reabre cuando cambia el archivo
let datos: { db: Db; mtime: number } | null = null;
function base(): Db | null {
  if (!existsSync(RUTA)) return null;
  const mtime = statSync(RUTA).mtimeMs;
  if (!datos || datos.mtime !== mtime) {
    datos?.db.close();
    datos = { db: new Database(RUTA, { readonly: true, fileMustExist: true }), mtime };
  }
  return datos.db;
}

const metaDe = (d: Db) => Object.fromEntries((d.prepare("SELECT clave, valor FROM meta").all() as { clave: string; valor: string }[]).map(x => [x.clave, x.valor]));
const medida = (t: Tot, universo: number) => ({
  filas: t.filas ?? 0, requests: t.req ?? 0, pct_universo: universo ? (t.req ?? 0) / universo : 0,
  pct_vendido: t.req ? (t.vend ?? 0) / t.req : null, ecpm: t.vend ? t.gasto / t.vend : null,
});

function leerFiltro(d: Db, b: any): Filtro | string {
  const paisesOk = new Set((d.prepare("SELECT DISTINCT pais FROM valores").all() as { pais: string }[]).map(x => x.pais));
  const pedidos: string[] = (Array.isArray(b?.paises) ? b.paises : []).map((x: unknown) => String(x));
  const paises = [...new Set(pedidos)].filter(p => paisesOk.has(p));
  if (!paises.length) return "Elige al menos un país";
  const cols = columnasBase(d);
  const existe = d.prepare("SELECT 1 FROM valores WHERE tipo = ? AND valor = ? LIMIT 1");
  const f = { paises, titulo: String(b?.titulo ?? "").trim().slice(0, 80), extras: [] as SenalExtra[] } as Filtro;
  for (const a of ATRIBUTOS) {
    // un content object puede traer varios valores separados por "|" (cualquiera de ellos): así los arma AI Deals
    const partes = [...new Set(String(b?.[a.tipo] ?? "").split("|").map(x => x.trim()).filter(Boolean))];
    if (partes.length && !cols.has(a.col)) return "La base de deals cargada es de una versión anterior y no trae ese content object: hay que regenerar deals.db";
    if (partes.length > 8) return `Demasiados valores para ${a.tipo}`;
    for (const v of partes) {
      if (("formato" in a && !a.formato.test(v)) || !existe.get(datoDe(a), v)) return `Valor desconocido para ${a.tipo}`;
    }
    f[a.tipo] = partes.join("|");
  }
  if (f.titulo && f.titulo.length < 3) return "Para buscar por título escribe al menos 3 letras";
  if (!f.titulo && !ATRIBUTOS.some(a => f[a.tipo])) return "Elige al menos un content object del reporte (género, categoría, serie…)";
  const extras = leerExtras(b?.extras);
  if (typeof extras === "string") return extras;
  f.extras = extras;
  if (senalesDe(f).length > MAX_SENALES) return `PubMatic admite máximo ${MAX_SENALES} señales en la regla que acompaña a la lista de títulos (el idioma cuenta como una)`;
  return f;
}

const cacheColumnas = new WeakMap<Db, Set<string>>();
function columnasBase(d: Db) {
  let c = cacheColumnas.get(d);
  if (!c) cacheColumnas.set(d, c = new Set((d.prepare("PRAGMA table_info(base)").all() as { name: string }[]).map(x => x.name)));
  return c;
}

/** Subconsulta con cada grupo del corte marcado: nat = lo alcanza el filtro nativo, lst = está en nuestra lista. */
function marcada(f: Filtro) {
  const args: Record<string, string> = {};
  f.paises.forEach((p, i) => { args[`p${i}`] = p; });
  const nat: string[] = [], lst = ["b.titulo <> ''"];
  for (const a of ATRIBUTOS) {
    const v = f[a.tipo];
    if (!v) continue;
    // varios valores separados por "|" = cualquiera de ellos
    const partes = v.split("|");
    partes.forEach((x, i) => { args[`l_${a.tipo}_${i}`] = `%;${escaparLike(x)};%`; args[`v_${a.tipo}_${i}`] = x; });
    const declara = "(" + partes.map((_, i) => `b.${a.col} LIKE @l_${a.tipo}_${i} ESCAPE '\\'`).join(" OR ") + ")";
    nat.push(declara);
    if (a.enriquecible) {
      lst.push(`EXISTS (SELECT 1 FROM titulo_attr t WHERE t.tipo = '${datoDe(a)}' AND t.valor IN (${partes.map((_, i) => `@v_${a.tipo}_${i}`).join(", ")}) AND t.titulo = b.titulo)`);
    } else lst.push(declara);
  }
  if (f.titulo) {
    // el título siempre viene del publisher: filtra igual en los dos caminos
    const contiene = "b.titulo LIKE @tq ESCAPE '\\'";
    args.tq = `%${escaparLike(f.titulo)}%`;
    nat.push(contiene); lst.push(contiene);
  }
  const sql = `(SELECT b.publisher, b.titulo, b.req, b.vend, b.gasto, b.filas, (${nat.join(" AND ")}) AS nat, (${lst.join(" AND ")}) AS lst
    FROM base b WHERE b.pais IN (${f.paises.map((_, i) => `@p${i}`).join(", ")}))`;
  return { sql, args };
}

/** Títulos de la lista por requests, recortados a lo que PubMatic acepta en un CSV. */
function titulosDe(d: Db, f: Filtro) {
  const { sql, args } = marcada(f);
  const todos = d.prepare(`SELECT titulo, SUM(req) req, SUM(vend) vend, SUM(gasto) gasto FROM ${sql} WHERE lst GROUP BY titulo ORDER BY req DESC, titulo`)
    .all(args) as { titulo: string; req: number; vend: number; gasto: number }[];
  const lineas: string[] = [];
  let bytes = 12, reqDentro = 0;
  for (const t of todos) {
    // PubMatic rechaza el archivo entero («invalid expressions») si un valor trae tres signos de exclamación seguidos
    if (/!!!|[\r\n]/.test(t.titulo)) continue;
    const linea = `"${t.titulo.replaceAll('"', '""')}"\r\n`, peso = Buffer.byteLength(linea);
    if (lineas.length >= MAX_VALORES || bytes + peso > MAX_BYTES) break;
    lineas.push(linea); bytes += peso; reqDentro += t.req;
  }
  return { todos, dentro: lineas.length, reqDentro, csv: '"Title_is"\r\n' + lineas.join("") };
}

function simular(d: Db, f: Filtro) {
  const { sql, args } = marcada(f);
  const suma = (cond: string, pre: string) => `COUNT(CASE WHEN ${cond} THEN 1 END) ${pre}_filas, SUM(CASE WHEN ${cond} THEN req END) ${pre}_req,
    SUM(CASE WHEN ${cond} THEN vend END) ${pre}_vend, SUM(CASE WHEN ${cond} THEN gasto END) ${pre}_gasto`;
  const r = d.prepare(`SELECT ${suma("1", "u")}, ${suma("nat", "n")}, ${suma("lst", "l")}, ${suma("nat OR lst", "x")},
    ${suma("lst AND NOT nat", "s")}, ${suma("nat AND NOT lst", "o")} FROM ${sql}`).get(args) as Record<string, number>;
  const tot = (pre: string): Tot => ({ filas: r[`${pre}_filas`], req: r[`${pre}_req`] ?? 0, vend: r[`${pre}_vend`] ?? 0, gasto: r[`${pre}_gasto`] ?? 0 });
  const u = tot("u"), t = titulosDe(d, f);
  // La recomendación es la unión: lo que ya alcanzan los filtros nativos (incluye lo que viene sin título, que
  // ninguna lista puede cubrir) más lo que agrega la lista de títulos. El precio lo fija la ruta de venta: por
  // publisher, lo que alcanza cada camino y a qué eCPM histórico
  const publishers = (d.prepare(`SELECT publisher,
      SUM(req) x_req, SUM(vend) x_vend, SUM(gasto) x_gasto,
      SUM(CASE WHEN nat THEN req END) n_req, SUM(CASE WHEN nat THEN vend END) n_vend, SUM(CASE WHEN nat THEN gasto END) n_gasto
    FROM ${sql} WHERE nat OR lst GROUP BY publisher ORDER BY x_req DESC LIMIT 10`).all(args) as any[])
    .map(p => ({
      publisher: p.publisher,
      recomendado: medida({ filas: 0, req: p.x_req ?? 0, vend: p.x_vend ?? 0, gasto: p.x_gasto ?? 0 }, tot("x").req),
      nativo: medida({ filas: 0, req: p.n_req ?? 0, vend: p.n_vend ?? 0, gasto: p.n_gasto ?? 0 }, tot("n").req),
    }));
  return {
    senales: senalesDe(f),
    filtro: f, universo: medida(u, u.req), nativo: medida(tot("n"), u.req), recomendado: medida(tot("x"), u.req),
    lista: medida(tot("l"), u.req), solo_lista: medida(tot("s"), u.req), solo_nativo: medida(tot("o"), u.req),
    titulos: {
      total: t.todos.length, en_csv: t.dentro, requests_en_csv: t.reqDentro, bytes_csv: Buffer.byteLength(t.csv),
      top: t.todos.slice(0, 10).map(x => ({ titulo: x.titulo, requests: x.req, pct_vendido: x.req ? x.vend / x.req : null, ecpm: x.vend ? x.gasto / x.vend : null })),
    },
    publishers,
  };
}

// ---- Trabajos de creación: uno a la vez (todos usan la misma cuenta de PubMatic)
interface Trabajo {
  id: number; usuario_id: number; nombre: string; filtro: string; estado: string; detalle: string;
  pm_id: string; enlace: string; titulos: number; creado: string; actualizado: string;
}
const cola: { id: number; nombre: string; paises: string[]; csv: string; condiciones: Condiciones; senales: SenalRegla[]; dsp?: string; seat?: string }[] = [];

/**
 * Señales que van tal cual a PubMatic en una segunda regla, unida con AND a la lista de títulos: las que solo
 * existen en PubMatic y el idioma (el reporte lo trae con los nombres estandarizados de PubMatic y nunca se
 * rellena). La estandarizada va al final: después de ella PubMatic no deja agregar más señales a la regla.
 */
function senalesDe(f: Filtro): SenalRegla[] {
  const out: SenalRegla[] = f.extras.map(e => ({ nombre: e.senal, modo: "manual", operador: e.operador, valores: e.valores }));
  if (f.idioma) out.push({ nombre: "Language", modo: "estandar", operador: "is", valores: [f.idioma] });
  return out;
}
let corriendo = false;

const RE_FECHA = /^\d{4}-\d{2}-\d{2}$/;
const esFecha = (s: string) => RE_FECHA.test(s) && !Number.isNaN(Date.parse(s + "T00:00:00Z")) && new Date(s + "T00:00:00Z").toISOString().slice(0, 10) === s;
const SIN_CONDICIONES: Condiciones = { inicio: "", fin: "", fee: "no", feeValor: 0, subasta: "first", mediaCpm: null };

/** Condiciones comerciales pedidas desde la web. Los límites finos (fee máximo, etc.) los valida PubMatic al llenar el asistente. */
function leerCondiciones(b: any): Condiciones | string {
  const x = b?.condiciones;
  if (x === undefined || x === null) return SIN_CONDICIONES;
  const inicio = String(x.inicio ?? "").trim(), fin = String(x.fin ?? "").trim();
  // PubMatic trabaja en hora del Pacífico: se admite desde "ayer" de aquí para no rechazar por el cambio de día
  const ayer = new Date(Date.now() - 864e5).toISOString().slice(0, 10);
  if (inicio && !esFecha(inicio)) return "Fecha de inicio inválida";
  if (fin && !esFecha(fin)) return "Fecha de fin inválida";
  if (inicio && inicio < ayer) return "La fecha de inicio ya pasó";
  if (fin && fin < (inicio || ayer)) return "La fecha de fin debe ser posterior a la de inicio";
  const fee = String(x.fee ?? "no");
  if (fee !== "no" && fee !== "fijo" && fee !== "porcentaje") return "Transaction fee inválido";
  const feeValor = fee === "no" ? 0 : Number(x.feeValor);
  if (fee === "fijo" && !(feeValor > 0 && feeValor <= 1000)) return "El transaction fee fijo debe ser un CPM en dólares mayor que 0";
  if (fee === "porcentaje" && !(feeValor > 0 && feeValor <= 100)) return "El transaction fee en porcentaje debe estar entre 0 y 100";
  const subasta = String(x.subasta ?? "first");
  if (subasta !== "first" && subasta !== "fixed") return "Tipo de subasta inválido";
  const vacio = x.mediaCpm === null || x.mediaCpm === undefined || x.mediaCpm === "";
  const mediaCpm = vacio ? null : Number(x.mediaCpm);
  if (mediaCpm !== null && !(mediaCpm > 0 && mediaCpm <= 1000)) return "El Media CPM debe ser un valor en dólares mayor que 0";
  if (subasta === "fixed" && mediaCpm === null) return "Fixed Price necesita un Media CPM";
  return { inicio, fin, fee, feeValor, subasta, mediaCpm };
}

export function rutasDeals(app: Hono<any>, db: Db) {
  db.exec(`CREATE TABLE IF NOT EXISTS deals_trabajos (
    id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), nombre TEXT NOT NULL, filtro TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('en_cola', 'corriendo', 'listo', 'error', 'sin_pausar')),
    detalle TEXT NOT NULL DEFAULT '', pm_id TEXT NOT NULL DEFAULT '', enlace TEXT NOT NULL DEFAULT '', titulos INTEGER NOT NULL DEFAULT 0,
    creado TEXT NOT NULL, actualizado TEXT NOT NULL)`);
  // condiciones comerciales pedidas (JSON) y lo que PubMatic mostró en su resumen; la tabla ya existía sin ellas
  const columnas = new Set((db.prepare("PRAGMA table_info(deals_trabajos)").all() as { name: string }[]).map(x => x.name));
  // AI Deals guarda además de dónde salió el deal: el brief, el plan que eligió el modelo, el DSP, la cuenta y el CPM
  for (const col of ["condiciones", "resumen_pm", "tipo", "brief", "plan", "dsp", "cuenta", "cpm"]) if (!columnas.has(col)) db.exec(`ALTER TABLE deals_trabajos ADD COLUMN ${col} TEXT NOT NULL DEFAULT ''`);
  const guardarResumen = db.prepare("UPDATE deals_trabajos SET resumen_pm = ? WHERE id = ?");
  // Si el servidor se reinició a medias no se sabe en qué quedó el deal: que alguien lo revise en PubMatic
  db.prepare(`UPDATE deals_trabajos SET estado = 'error', detalle = 'El servidor se reinició mientras corría. Revisa en PubMatic > Deals si el deal se creó y si está en pausa.'
    WHERE estado IN ('en_cola', 'corriendo')`).run();
  const marcar = db.prepare("UPDATE deals_trabajos SET estado = ?, detalle = ?, pm_id = ?, enlace = ?, actualizado = ? WHERE id = ?");
  const ahora = () => new Date().toISOString();

  async function atender() {
    if (corriendo) return;
    corriendo = true;
    for (let t = cola.shift(); t; t = cola.shift()) {
      const { id } = t;
      try {
        marcar.run("corriendo", "Empezando", "", "", ahora(), id);
        const r = await crearDeal({ nombre: t.nombre, paises: t.paises, titulosCsv: t.csv, condiciones: t.condiciones, senales: t.senales, dsp: t.dsp, seat: t.seat },
          msg => marcar.run("corriendo", msg, "", "", ahora(), id));
        guardarResumen.run(r.resumen, id);
        if (r.estado === "ensayo") marcar.run("error", "Ensayo: el bot recorrió todo el asistente y se detuvo en el resumen. No se creó nada.", "", "", ahora(), id);
        else marcar.run("listo", `Creado y en pausa (${r.estado})`, r.pmId, r.enlace, ahora(), id);
      } catch (e) {
        const sinPausar = e instanceof DealSinPausar;
        marcar.run(sinPausar ? "sin_pausar" : "error", (e as Error).message.split("\n")[0].slice(0, 500), sinPausar ? e.pmId : "", "", ahora(), id);
        console.error(`deal ${t.nombre}:`, e);
      }
    }
    corriendo = false;
  }

  app.get("/api/admin/deals/opciones", c => {
    const d = base();
    if (!d) return c.json({ error: "Todavía no se ha cargado la base de deals (deals.db)" }, 503);
    const vals = d.prepare("SELECT tipo, valor, pais, req FROM valores ORDER BY req DESC").all() as { tipo: string; valor: string; pais: string; req: number }[];
    const juntar = (tipo: string) => {
      const m = new Map<string, { valor: string; requests: number; paises: Record<string, number> }>();
      for (const v of vals) if (v.tipo === tipo) {
        const x = m.get(v.valor) ?? { valor: v.valor, requests: 0, paises: {} };
        x.requests += v.req; x.paises[v.pais] = v.req; m.set(v.valor, x);
      }
      return [...m.values()].sort((a, b) => b.requests - a.requests);
    };
    const paises = d.prepare("SELECT pais, SUM(req) requests FROM base GROUP BY pais ORDER BY requests DESC").all();
    const cols = columnasBase(d);
    const total = (paises as { requests: number }[]).reduce((t, x) => t + x.requests, 0);
    const ETIQUETA: Record<string, Record<string, string>> = {
      envivo: { "1": "Sí, en vivo", "0": "No" }, con_titulo: { true: "Sí", false: "No" },
    };
    // los demás content objects del reporte (si la base cargada ya los trae); la serie se recorta a las de más requests
    const otros = Object.fromEntries(ATRIBUTOS.filter(a => a.tipo !== "genero" && datoDe(a) !== "categoria" && cols.has(a.col)).map(a => [a.tipo,
      juntar(a.tipo).filter(x => a.tipo !== "rating" || x.requests >= 0.0005 * total)   // sin la cola de clasificaciones sueltas de cada país
        .slice(0, a.tipo === "serie" ? 600 : 60).map(x => ({ ...x, nombre: ETIQUETA[a.tipo]?.[x.valor] ?? "" }))]));
    const categorias = juntar("categoria").map(x => {
      const s = significadoCategoria(`[${x.valor}]`)[0];
      return { ...x, nombre: s ? s.es || s.en : "" };
    });
    return c.json({
      atributos: otros, enriquecibles: ATRIBUTOS.filter(a => a.enriquecible).map(a => a.tipo), senales_pubmatic: SENALES_PUBMATIC,
      meta: metaDe(d), paises, generos: juntar("genero"),
      categorias: categorias.filter(x => /^IAB\d/.test(x.valor)),
      categorias_num: categorias.filter(x => /^\d+$/.test(x.valor)),
      max_senales: MAX_SENALES,
      pubmatic: { configurado: pubmaticConfigurado(), dsp: PUBMATIC.dsp, buyer: PUBMATIC.buyer, ensayo: PUBMATIC.ensayo },
    });
  });

  app.post("/api/admin/deals/simular", async c => {
    const d = base();
    if (!d) return c.json({ error: "Todavía no se ha cargado la base de deals (deals.db)" }, 503);
    const f = leerFiltro(d, await c.req.json().catch(() => null));
    if (typeof f === "string") return c.json({ error: f }, 400);
    return c.json(simular(d, f));
  });

  app.post("/api/admin/deals/titulos.csv", async c => {
    const d = base();
    if (!d) return c.json({ error: "Todavía no se ha cargado la base de deals (deals.db)" }, 503);
    const f = leerFiltro(d, await c.req.json().catch(() => null));
    if (typeof f === "string") return c.json({ error: f }, 400);
    c.header("Content-Type", "text/csv; charset=utf-8");
    c.header("Content-Disposition", 'attachment; filename="Title_is.csv"');
    return c.body(titulosDe(d, f).csv);
  });

  app.get("/api/admin/deals/trabajos", c => c.json({
    trabajos: (db.prepare(`SELECT t.*, u.nombre AS de FROM deals_trabajos t JOIN usuarios u ON u.id = t.usuario_id ORDER BY t.id DESC LIMIT 30`).all() as (Trabajo & { de: string })[])
      .map(t => ({ ...t, filtro: JSON.parse(t.filtro), condiciones: (t as any).condiciones ? JSON.parse((t as any).condiciones) : null,
        plan: (t as any).plan ? JSON.parse((t as any).plan) : null })),
  }));

  app.post("/api/admin/deals/crear", async c => {
    const d = base();
    if (!d) return c.json({ error: "Todavía no se ha cargado la base de deals (deals.db)" }, 503);
    if (!pubmaticConfigurado()) return c.json({ error: "El servidor no tiene configuradas las credenciales de PubMatic" }, 503);
    const b = await c.req.json().catch(() => null);
    const f = leerFiltro(d, b);
    if (typeof f === "string") return c.json({ error: f }, 400);
    const nombre = String(b?.nombre ?? "").trim();
    if (!RE_NOMBRE.test(nombre)) return c.json({ error: "Nombre del deal: de 3 a 100 caracteres, solo letras, números, espacios, punto, guion y guion bajo" }, 400);
    const cond = leerCondiciones(b);
    if (typeof cond === "string") return c.json({ error: cond }, 400);
    if (b?.confirmo !== true) return c.json({ error: "Falta confirmar la creación" }, 400);
    if (db.prepare("SELECT 1 FROM deals_trabajos WHERE nombre = ? AND estado IN ('en_cola', 'corriendo', 'listo', 'sin_pausar')").get(nombre)) {
      return c.json({ error: "Ya se creó (o se está creando) un deal con ese nombre" }, 409);
    }
    const t = titulosDe(d, f);
    if (!t.dentro) return c.json({ error: "Ese filtro no tiene títulos que recomendar" }, 400);
    const id = Number(db.prepare(`INSERT INTO deals_trabajos (usuario_id, nombre, filtro, condiciones, estado, detalle, titulos, creado, actualizado)
      VALUES (?, ?, ?, ?, 'en_cola', 'En cola', ?, ?, ?)`).run(c.get("u").id, nombre, JSON.stringify(f), JSON.stringify(cond), t.dentro, ahora(), ahora()).lastInsertRowid);
    cola.push({ id, nombre, paises: f.paises, csv: t.csv, condiciones: cond, senales: senalesDe(f) });
    void atender();
    return c.json({ id });
  });

  // ---- AI Deals: el brief de la campaña decide los content objects; el CPM se reparte 50/50 entre fee y puja
  const CAMPANAS = ["Connected TV (CTV)"], FORMATOS = ["Video"];   // por ahora las únicas que arma el bot
  const CPM_MIN = 1, CPM_MAX = 20;   // mitad y mitad: la puja no baja del piso de $0.50 y el fee fijo no pasa de $10
  const RE_CUENTA = /^[A-Za-z0-9][A-Za-z0-9._-]{1,39}$/;

  const paisesAi = (d: Db) => (d.prepare("SELECT pais FROM base GROUP BY pais ORDER BY SUM(req) DESC").all() as { pais: string }[]).map(x => x.pais);

  /** Los campos que llena la persona: brief, DSP, cuenta, CPM, mercado (país), tipo de campaña y formato. */
  function leerEntradaAi(d: Db, b: any) {
    const brief = String(b?.brief ?? "").trim();
    if (brief.length < 20) return "Escribe el brief de la campaña (al menos un par de frases)";
    if (brief.length > 6000) return "El brief es demasiado largo (máximo 6,000 caracteres)";
    const dsp = String(b?.dsp ?? "").trim();
    if (!(DSPS as readonly string[]).includes(dsp)) return "Elige el DSP de la lista";
    const cuenta = String(b?.cuenta ?? "").trim();
    if (!RE_CUENTA.test(cuenta)) return "Escribe el ID de la cuenta (seat ID)";
    const pais = String(b?.pais ?? "").trim();
    if (!paisesAi(d).includes(pais)) return "Elige el mercado de la lista";
    const cpm = Number(b?.cpm);
    if (!Number.isFinite(cpm)) return "Escribe el CPM en dólares";
    if (Math.abs(Math.round(cpm * 100) - cpm * 100) > 1e-6) return "El CPM admite máximo dos decimales";
    if (cpm < CPM_MIN || cpm > CPM_MAX) return `El CPM debe estar entre $${CPM_MIN} y $${CPM_MAX}`;
    if (!CAMPANAS.includes(String(b?.campana ?? ""))) return "Tipo de campaña no disponible";
    if (!FORMATOS.includes(String(b?.formato ?? ""))) return "Formato no disponible";
    return { brief, dsp, cuenta, pais, cpm: Math.round(cpm * 100) / 100 };
  }

  /** CPM total -> mitad fee fijo y mitad Media CPM a precio fijo (como se configura a mano en PubMatic). */
  function condicionesDeCpm(cpm: number): Condiciones {
    const fee = Math.round(cpm * 50) / 100;
    return { inicio: "", fin: "", fee: "fijo", feeValor: fee, subasta: "fixed", mediaCpm: Math.round((cpm - fee) * 100) / 100 };
  }

  /** Lo que el modelo puede elegir: lo que hay en el corte vigente para ese mercado, con su peso en requests. */
  function catalogoAi(d: Db, pais: string): Catalogo {
    const total = (d.prepare("SELECT SUM(req) r FROM base WHERE pais = ?").get(pais) as { r: number }).r || 1;
    const de = (tipo: string, n: number, formato?: RegExp) => (d.prepare("SELECT valor, SUM(req) r FROM valores WHERE tipo = ? AND pais = ? GROUP BY valor ORDER BY r DESC").all(tipo, pais) as { valor: string; r: number }[])
      .filter(x => !formato || formato.test(x.valor)).slice(0, n).map(x => ({ valor: x.valor, pct: 100 * x.r / total }));
    return {
      generos: de("genero", 40).filter(x => !["otros/desconocido"].includes(x.valor)),
      categorias: de("categoria", 30, /^IAB\d/).map(x => ({ ...x, nombre: significadoCategoria(`[${x.valor}]`)[0]?.es || undefined })),
      ratings: de("rating", 5), idiomas: de("idioma", 12),
    };
  }

  /** El plan del modelo como filtro del armador: varios valores de un mismo content object van unidos con "|". */
  const filtroDePlan = (d: Db, plan: PlanBrief) => leerFiltro(d, {
    paises: plan.paises, genero: plan.generos.join("|"), categoria: plan.categorias.join("|"), rating: plan.ratings.join("|"), idioma: plan.idioma,
  });

  function leerPlan(x: any): PlanBrief | string {
    const textos = (v: unknown, n: number) => (Array.isArray(v) ? v : []).map(y => String(y).trim()).filter(Boolean).slice(0, n);
    const plan: PlanBrief = {
      paises: textos(x?.paises, 20), generos: textos(x?.generos, 8), categorias: textos(x?.categorias, 8), ratings: textos(x?.ratings, 8),
      idioma: String(x?.idioma ?? "").trim(), palabras_clave: textos(x?.palabras_clave, 4).map(k => k.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")).filter(Boolean),
      razon: String(x?.razon ?? "").slice(0, 900),
    };
    return plan.paises.length ? plan : "El plan no trae países";
  }

  /** Nombre genérico del deal: palabras clave del brief + lo que se llenó, en minúsculas y con guiones. */
  function nombreAi(plan: PlanBrief, dsp: string, cpm: number) {
    const limpio = (t: string) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    const claves = (plan.palabras_clave.length ? plan.palabras_clave : plan.generos).slice(0, 4).map(limpio).filter(Boolean);
    const hoy = new Date().toISOString().replace(/[-:T]/g, "").slice(4, 12);   // MMDDHHmm: evita repetir nombres
    return [...claves, "ctv", "video", limpio(dsp), `${String(cpm).replace(".", "-")}usd`, hoy].join("-").slice(0, 100);
  }

  /** Lo que se muestra antes de crear: qué eligió el modelo y cuánto inventario hay detrás. */
  function vistaPlan(d: Db, plan: PlanBrief, f: Filtro, dsp: string, cpm: number) {
    const sim = simular(d, f), cond = condicionesDeCpm(cpm);
    return {
      plan, filtro: f, nombre: nombreAi(plan, dsp, cpm), cpm, fee: cond.feeValor, media_cpm: cond.mediaCpm,
      nativo: sim.nativo, recomendado: sim.recomendado, lista: sim.lista,
      titulos: { total: sim.titulos.total, en_csv: sim.titulos.en_csv, top: sim.titulos.top },
      categorias: plan.categorias.map(c => ({ valor: c, nombre: significadoCategoria(`[${c}]`)[0]?.es ?? "" })),
    };
  }

  app.get("/api/admin/deals/ai/opciones", c => {
    const d = base();
    return c.json({
      dsps: DSPS, dsp_defecto: PUBMATIC.dsp, campanas: CAMPANAS, formatos: FORMATOS, cpm: { min: CPM_MIN, max: CPM_MAX },
      meta: d ? metaDe(d) : null, paises: d ? paisesAi(d) : [],
      configurado: { datos: !!d, ai: aiConfigurado(), pubmatic: pubmaticConfigurado(), ensayo: PUBMATIC.ensayo },
    });
  });

  app.post("/api/admin/deals/ai/plan", async c => {
    const d = base();
    if (!d) return c.json({ error: "Todavía no se ha cargado la base de deals (deals.db)" }, 503);
    if (!aiConfigurado()) return c.json({ error: "El servidor no tiene configurada la llave del modelo que lee el brief (ANTHROPIC_API_KEY o GROQ_API_KEY)" }, 503);
    const e = leerEntradaAi(d, await c.req.json().catch(() => null));
    if (typeof e === "string") return c.json({ error: e }, 400);
    let plan: PlanBrief;
    try {
      plan = await interpretarBrief(e.brief, catalogoAi(d, e.pais), e.pais);
    } catch (err) {
      if (err instanceof ErrorAi) return c.json({ error: err.message }, 502);
      console.error("ai deals:", err);
      return c.json({ error: "No se pudo interpretar el brief" }, 500);
    }
    if (!plan.generos.length && !plan.categorias.length && !plan.ratings.length && !plan.idioma) {
      return c.json({ error: "El modelo no encontró en el brief ningún content object con el cual filtrar. Describe mejor el producto, el público o el tipo de contenido." }, 422);
    }
    const f = filtroDePlan(d, plan);
    if (typeof f === "string") return c.json({ error: f }, 502);
    return c.json(vistaPlan(d, plan, f, e.dsp, e.cpm));
  });

  app.post("/api/admin/deals/ai/crear", async c => {
    const d = base();
    if (!d) return c.json({ error: "Todavía no se ha cargado la base de deals (deals.db)" }, 503);
    if (!pubmaticConfigurado()) return c.json({ error: "El servidor no tiene configuradas las credenciales de PubMatic" }, 503);
    const b = await c.req.json().catch(() => null);
    const e = leerEntradaAi(d, b);
    if (typeof e === "string") return c.json({ error: e }, 400);
    const plan = leerPlan({ ...b?.plan, paises: [e.pais] });   // el mercado lo decide la persona, no el plan
    if (typeof plan === "string") return c.json({ error: plan }, 400);
    const f = filtroDePlan(d, plan);   // vuelve a validar contra el catálogo lo que manda el navegador
    if (typeof f === "string") return c.json({ error: f }, 400);
    if (b?.confirmo !== true) return c.json({ error: "Falta confirmar la creación" }, 400);
    const t = titulosDe(d, f);
    if (!t.dentro) return c.json({ error: "Con esos content objects no hay títulos en el inventario: no hay con qué armar el deal" }, 400);
    const nombre = nombreAi(plan, e.dsp, e.cpm), cond = condicionesDeCpm(e.cpm);
    if (db.prepare("SELECT 1 FROM deals_trabajos WHERE nombre = ? AND estado IN ('en_cola', 'corriendo', 'listo', 'sin_pausar')").get(nombre)) {
      return c.json({ error: "Ya se está creando un deal con ese nombre; espera un minuto e intenta de nuevo" }, 409);
    }
    const id = Number(db.prepare(`INSERT INTO deals_trabajos (usuario_id, nombre, filtro, condiciones, estado, detalle, titulos, creado, actualizado, tipo, brief, plan, dsp, cuenta, cpm)
      VALUES (?, ?, ?, ?, 'en_cola', 'En cola', ?, ?, ?, 'ai', ?, ?, ?, ?, ?)`).run(c.get("u").id, nombre, JSON.stringify(f), JSON.stringify(cond), t.dentro, ahora(), ahora(),
      e.brief, JSON.stringify(plan), e.dsp, e.cuenta, String(e.cpm)).lastInsertRowid);
    cola.push({ id, nombre, paises: f.paises, csv: t.csv, condiciones: cond, senales: senalesDe(f), dsp: e.dsp, seat: e.cuenta });
    void atender();
    return c.json({ id, nombre });
  });
}
