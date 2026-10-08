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
import { crearDeal, DealSinPausar, PUBMATIC, pubmaticConfigurado } from "./pubmatic.js";

const RUTA = process.env.DEALS_DB ?? "/data/deals.db";
const MAX_VALORES = 10_000;       // valores por deal en la carga por CSV de PubMatic
const MAX_BYTES = 500 * 1000;     // tamaño máximo del CSV
const RE_NOMBRE = /^[A-Za-z0-9][A-Za-z0-9 ._-]{2,99}$/;

type Db = InstanceType<typeof Database>;
interface Tot { filas: number; req: number; vend: number; gasto: number }
interface Filtro { paises: string[]; genero: string; categoria: string }

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
  const genero = String(b?.genero ?? "").trim(), categoria = String(b?.categoria ?? "").trim();
  if (!paises.length) return "Elige al menos un país";
  if (!genero && !categoria) return "Elige un género, una categoría o los dos";
  const existe = d.prepare("SELECT 1 FROM valores WHERE tipo = ? AND valor = ? LIMIT 1");
  if (genero && !existe.get("genero", genero)) return "Género desconocido";
  if (categoria && !existe.get("categoria", categoria)) return "Categoría desconocida";
  return { paises, genero, categoria };
}

/** Subconsulta con cada grupo del corte marcado: nat = lo alcanza el filtro nativo, lst = está en nuestra lista. */
function marcada(f: Filtro) {
  const args: Record<string, string> = {};
  f.paises.forEach((p, i) => { args[`p${i}`] = p; });
  const nat: string[] = [], lst = ["b.titulo <> ''"];
  if (f.genero) {
    nat.push("b.gen_decl LIKE @gl");
    lst.push("EXISTS (SELECT 1 FROM titulo_attr t WHERE t.tipo = 'genero' AND t.valor = @g AND t.titulo = b.titulo)");
    args.g = f.genero; args.gl = `%;${f.genero};%`;
  }
  if (f.categoria) {
    nat.push("b.cat_decl LIKE @cl");
    lst.push("EXISTS (SELECT 1 FROM titulo_attr t WHERE t.tipo = 'categoria' AND t.valor = @c AND t.titulo = b.titulo)");
    args.c = f.categoria; args.cl = `%;${f.categoria};%`;
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
    FROM ${sql} WHERE nat OR lst GROUP BY publisher ORDER BY x_req DESC LIMIT 15`).all(args) as any[])
    .map(p => ({
      publisher: p.publisher,
      recomendado: medida({ filas: 0, req: p.x_req ?? 0, vend: p.x_vend ?? 0, gasto: p.x_gasto ?? 0 }, tot("x").req),
      nativo: medida({ filas: 0, req: p.n_req ?? 0, vend: p.n_vend ?? 0, gasto: p.n_gasto ?? 0 }, tot("n").req),
    }));
  return {
    filtro: f, universo: medida(u, u.req), nativo: medida(tot("n"), u.req), recomendado: medida(tot("x"), u.req),
    lista: medida(tot("l"), u.req), solo_lista: medida(tot("s"), u.req), solo_nativo: medida(tot("o"), u.req),
    titulos: {
      total: t.todos.length, en_csv: t.dentro, requests_en_csv: t.reqDentro, bytes_csv: Buffer.byteLength(t.csv),
      top: t.todos.slice(0, 40).map(x => ({ titulo: x.titulo, requests: x.req, pct_vendido: x.req ? x.vend / x.req : null, ecpm: x.vend ? x.gasto / x.vend : null })),
    },
    publishers,
  };
}

// ---- Trabajos de creación: uno a la vez (todos usan la misma cuenta de PubMatic)
interface Trabajo {
  id: number; usuario_id: number; nombre: string; filtro: string; estado: string; detalle: string;
  pm_id: string; enlace: string; titulos: number; creado: string; actualizado: string;
}
const cola: { id: number; nombre: string; paises: string[]; csv: string }[] = [];
let corriendo = false;

export function rutasDeals(app: Hono<any>, db: Db) {
  db.exec(`CREATE TABLE IF NOT EXISTS deals_trabajos (
    id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), nombre TEXT NOT NULL, filtro TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('en_cola', 'corriendo', 'listo', 'error', 'sin_pausar')),
    detalle TEXT NOT NULL DEFAULT '', pm_id TEXT NOT NULL DEFAULT '', enlace TEXT NOT NULL DEFAULT '', titulos INTEGER NOT NULL DEFAULT 0,
    creado TEXT NOT NULL, actualizado TEXT NOT NULL)`);
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
        const r = await crearDeal({ nombre: t.nombre, paises: t.paises, titulosCsv: t.csv }, msg => marcar.run("corriendo", msg, "", "", ahora(), id));
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
    return c.json({
      meta: metaDe(d), paises, generos: juntar("genero"),
      categorias: juntar("categoria").filter(x => /^IAB\d/.test(x.valor)).map(x => {
        const s = significadoCategoria(`[${x.valor}]`)[0];
        return { ...x, nombre: s ? s.es || s.en : "" };
      }),
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
      .map(t => ({ ...t, filtro: JSON.parse(t.filtro) })),
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
    if (b?.confirmo !== true) return c.json({ error: "Falta confirmar la creación" }, 400);
    if (db.prepare("SELECT 1 FROM deals_trabajos WHERE nombre = ? AND estado IN ('en_cola', 'corriendo', 'listo', 'sin_pausar')").get(nombre)) {
      return c.json({ error: "Ya se creó (o se está creando) un deal con ese nombre" }, 409);
    }
    const t = titulosDe(d, f);
    if (!t.dentro) return c.json({ error: "Ese filtro no tiene títulos que recomendar" }, 400);
    const id = Number(db.prepare(`INSERT INTO deals_trabajos (usuario_id, nombre, filtro, estado, detalle, titulos, creado, actualizado)
      VALUES (?, ?, ?, 'en_cola', 'En cola', ?, ?, ?)`).run(c.get("u").id, nombre, JSON.stringify(f), t.dentro, ahora(), ahora()).lastInsertRowid);
    cola.push({ id, nombre, paises: f.paises, csv: t.csv });
    void atender();
    return c.json({ id });
  });
}
