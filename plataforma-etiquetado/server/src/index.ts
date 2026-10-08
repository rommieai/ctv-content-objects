import { readFileSync } from "node:fs";
import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono, type Context } from "hono";
import { deleteCookie, getCookie, setCookie } from "hono/cookie";
import { abrir, DIR_IAB } from "./db.js";
import { hashToken, nuevoToken, verificarClave } from "./auth.js";
import { cargarIab } from "./significados.js";
import { rutasDeals } from "./deals.js";
import { CAMPOS, construirRegistro, FICHA, llaves, NOMBRE_CAMPO, ORIGINAL, PREVIO, type Campo, type Fila, type Registro } from "./registros.js";

interface Usuario { id: number; usuario: string; nombre: string; rol: "admin" | "revisor" }
type Env = { Variables: { u: Usuario } };

const PUERTO = Number(process.env.PORT ?? 3000);
const DIR_PUBLICO = process.env.PUBLIC_DIR ?? "./public";
const DIAS_SESION = 30;
const POR_PAGINA = 20;

cargarIab(DIR_IAB);
const db = abrir();
if (!db.prepare("SELECT 1 FROM sqlite_master WHERE name = 'meta'").get()) {
  console.error("La base no tiene datos: corre primero el importador (ver README).");
  process.exit(1);
}
const meta = Object.fromEntries((db.prepare("SELECT clave, valor FROM meta").all() as { clave: string; valor: string }[])
  .map(x => [x.clave, x.valor]));
const VERSION: string = meta.version;
const MUESTRA_META = JSON.parse(meta.muestra_meta);
const TOTALES: Record<string, { filas: number; requests: number }> = JSON.parse(meta.totales_estrato);
const PAISES: string[] = JSON.parse(meta.paises);
const COLUMNAS: string[] = JSON.parse(meta.columnas);

// ---- La muestra es fija: se arma una vez en memoria
const MUESTRA: Registro[] = (db.prepare(`SELECT m.id, m.fila_id, m.campos, m.extra, m.ayuda, f.titulo, f.app_name,
    f.page_url, f.publisher, f.country, f.total_requests FROM muestra m JOIN filas f ON f.id = m.fila_id ORDER BY m.id`).all() as any[])
  .map(x => ({
    fila_id: x.fila_id, muestra_id: x.id, titulo: x.titulo, app: x.app_name, bundle: x.page_url, publisher: x.publisher,
    pais: x.country, requests: x.total_requests, campos: JSON.parse(x.campos) as Campo[],
    extra: x.extra ? JSON.parse(x.extra) : null, ayuda: JSON.parse(x.ayuda),
  }));
const MUESTRA_POR_FILA = new Map(MUESTRA.map(r => [r.fila_id, r]));
// "fila|campo|valor" -> estrato, para cada valor llenado de la muestra
const ESTRATO_MUESTRA = new Map<string, string>();
for (const r of MUESTRA) for (const c of r.campos) if (c.llenado) for (const u of c.unidades) ESTRATO_MUESTRA.set(`${r.fila_id}|${c.campo}|${u.valor}`, u.estrato);
const TOTAL_MUESTRA = ESTRATO_MUESTRA.size;
const FILAS_LLENADAS = (db.prepare("SELECT COUNT(*) n FROM filas WHERE n_unidades > 0").get() as { n: number }).n;
const ESTRATOS = Object.keys(TOTALES).sort();

const filaPorId = db.prepare("SELECT * FROM filas WHERE id = ?");
function registroDe(filaId: number): Registro | null {
  const m = MUESTRA_POR_FILA.get(filaId);
  if (m) return m;
  const f = filaPorId.get(filaId) as Fila | undefined;
  return f ? construirRegistro(f) : null;
}

// ---- Etiquetas del usuario
const qHechosMuestra = db.prepare(`SELECT e.fila_id, e.campo, e.valor FROM etiquetas e JOIN filas f ON f.id = e.fila_id
  WHERE e.usuario_id = ? AND f.en_muestra = 1`);
function hechosMuestra(uid: number) {
  return new Set((qHechosMuestra.all(uid) as any[]).map(x => `${x.fila_id}|${x.campo}|${x.valor}`));
}
const pendientes = (r: Registro, hechos: Set<string>) => llaves(r.campos).filter(k => !hechos.has(`${r.fila_id}|${k}`)).length;

function conEtiquetas(regs: Registro[], uid: number, admin: boolean) {
  if (!regs.length) return [];
  const ids = regs.map(r => r.fila_id);
  const marcas = ids.map(() => "?").join(",");
  const etq = db.prepare(`SELECT fila_id, campo, valor, veredicto, valor_correcto, actualizado FROM etiquetas
    WHERE usuario_id = ? AND fila_id IN (${marcas})`).all(uid, ...ids) as any[];
  const notas = new Map((db.prepare(`SELECT fila_id, nota FROM notas WHERE usuario_id = ? AND fila_id IN (${marcas})`)
    .all(uid, ...ids) as any[]).map(x => [x.fila_id, x.nota]));
  const crudas = admin ? new Map((db.prepare(`SELECT * FROM filas WHERE id IN (${marcas})`).all(...ids) as Fila[]).map(f => [f.id, f])) : null;
  return regs.map(r => {
    const mias: Record<string, { veredicto: string; correcto: string; ts: string }> = {};
    for (const e of etq) if (e.fila_id === r.fila_id) mias[`${e.campo}|${e.valor}`] = { veredicto: e.veredicto, correcto: e.valor_correcto, ts: e.actualizado };
    const f = crudas?.get(r.fila_id);
    return {
      ...r, etiquetas: mias, nota: notas.get(r.fila_id) ?? "",
      crudo: f ? Object.fromEntries(COLUMNAS.map(c => [c, f[c]])) : undefined,
    };
  });
}

// ---- Consultas del consolidado completo
const ORIGENES_EXTERNOS = "('imdb','wikidata','tvmaze','derivado_tipo')";
const SQL_EXTRA = `(ext_imdb_id <> '' AND (${CAMPOS.map(c => `"${c}_origen" IN ${ORIGENES_EXTERNOS}`).join(" OR ")}
  OR contentCategory_afinado_origen IN ('imdb','wikidata')))`;
const SQL_MIAS = "(SELECT COUNT(*) FROM etiquetas e WHERE e.usuario_id = @u AND e.fila_id = filas.id AND substr(e.campo, 1, 1) <> '_')";
const cacheConteos = new Map<string, number>();

function filtroCompleto(p: Record<string, string>, uid: number) {
  const w: string[] = [], args: Record<string, any> = {};
  if (p.llenados !== "0") w.push("n_unidades > 0");
  if ((CAMPOS as readonly string[]).includes(p.campo)) w.push(`"${p.campo}_origen" NOT IN ('', 'original')`);
  else if (p.campo === "_extra") w.push(SQL_EXTRA);
  if (p.estrato && TOTALES[p.estrato]) {
    const [campo, origen] = p.estrato.split("|");
    w.push(`"${campo}_origen" = @origen`);
    args.origen = origen;
  }
  if (p.q?.trim()) { w.push("(titulo LIKE @q OR app_name LIKE @q)"); args.q = `%${p.q.trim()}%`; }
  if (p.pais) { w.push("country = @pais"); args.pais = p.pais; }
  if (p.muestra === "1") w.push("en_muestra = 1");
  const clave = JSON.stringify([w, args]);
  if (p.estado === "pendientes") { w.push(`n_unidades > ${SQL_MIAS}`); args.u = uid; }
  else if (p.estado === "revisadas") {
    w.push(`n_unidades > 0 AND id IN (SELECT fila_id FROM etiquetas WHERE usuario_id = @u) AND n_unidades <= ${SQL_MIAS}`);
    args.u = uid;
  }
  return { where: w.length ? "WHERE " + w.join(" AND ") : "", args, clave: p.estado === "pendientes" || p.estado === "revisadas" ? null : clave };
}

function filtrarMuestra(p: Record<string, string>, hechos: Set<string>) {
  const q = (p.q ?? "").trim().toLowerCase();
  return MUESTRA.filter(r => {
    const us = r.campos.filter(c => c.llenado).flatMap(c => c.unidades.map(u => ({ ...u, campo: c.campo })));
    const pend = pendientes(r, hechos);
    return (!p.estado || p.estado === "todos" || (p.estado === "pendientes" ? pend > 0 : pend === 0)) &&
      (!p.campo || (p.campo === "_extra" ? !!r.extra : us.some(u => u.campo === p.campo))) &&
      (!p.estrato || us.some(u => u.estrato === p.estrato)) &&
      (!p.pais || r.pais === p.pais) &&
      (!q || `${r.titulo} ${r.app}`.toLowerCase().includes(q));
  });
}

// ---- Precisión por estrato (misma cuenta que scripts/calcular_precision_revision.py)
function wilson(ok: number, n: number, z = 1.96) {
  if (!n) return { p: null, lo: null, hi: null };
  const p = ok / n, den = 1 + z * z / n, centro = (p + z * z / (2 * n)) / den;
  const margen = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den;
  return { p, lo: Math.max(0, centro - margen), hi: Math.min(1, centro + margen) };
}
function estratoDe(filaId: number, campo: string, valor: string) {
  return campo === FICHA ? FICHA : ESTRATO_MUESTRA.get(`${filaId}|${campo}|${valor}`);
}
function precision(veredictos: Map<string, string>) {
  const cnt: Record<string, Record<string, number>> = {};
  const tot: Record<string, number> = {};
  for (const [k, e] of ESTRATO_MUESTRA) {
    tot[e] = (tot[e] ?? 0) + 1;
    const v = veredictos.get(k);
    if (v) (cnt[e] ??= {})[v] = (cnt[e]?.[v] ?? 0) + 1;
  }
  const fichas = MUESTRA.filter(r => r.extra);
  tot[FICHA] = fichas.length;
  for (const r of fichas) {
    const v = veredictos.get(`${r.fila_id}|${FICHA}|${r.extra.imdb_id}`);
    if (v) (cnt[FICHA] ??= {})[v] = (cnt[FICHA]?.[v] ?? 0) + 1;
  }
  const req = MUESTRA_META.totales_estrato as Record<string, { requests: number }>;
  return Object.keys(tot).sort().map(e => {
    const c = cnt[e] ?? {}, ok = c.correcto ?? 0, mal = c.incorrecto ?? 0, nss = c.no_se_sabe ?? 0;
    const w = wilson(ok, ok + mal), requests = req[e]?.requests ?? 0;
    return {
      estrato: e, total: tot[e], revisados: ok + mal, correctos: ok, incorrectos: mal, no_se_sabe: nss,
      pendientes: tot[e] - ok - mal - nss, precision: w.p, ic95: [w.lo, w.hi], requests_estrato: requests,
      requests_probablemente_mal: w.p === null ? null : Math.round((1 - w.p) * requests),
    };
  });
}

// ---- App
const app = new Hono<Env>();
const fallos = new Map<string, { n: number; desde: number }>();
const ip = (c: Context) => c.req.header("x-real-ip") ?? c.req.header("x-forwarded-for")?.split(",")[0].trim() ?? "local";

db.prepare("DELETE FROM sesiones WHERE expira < ?").run(Date.now());

app.post("/api/login", async c => {
  const quien = ip(c), f = fallos.get(quien);
  if (f && f.n >= 10 && Date.now() - f.desde < 15 * 60_000) return c.json({ error: "Demasiados intentos; espera unos minutos" }, 429);
  const { usuario, clave } = await c.req.json().catch(() => ({}));
  const u = db.prepare("SELECT * FROM usuarios WHERE usuario = ?").get(String(usuario ?? "").trim().toLowerCase()) as any;
  if (!u || !verificarClave(String(clave ?? ""), u.clave)) {
    fallos.set(quien, f && Date.now() - f.desde < 15 * 60_000 ? { n: f.n + 1, desde: f.desde } : { n: 1, desde: Date.now() });
    return c.json({ error: "Usuario o contraseña incorrectos" }, 401);
  }
  fallos.delete(quien);
  const token = nuevoToken();
  db.prepare("INSERT INTO sesiones (token, usuario_id, expira) VALUES (?, ?, ?)").run(hashToken(token), u.id, Date.now() + DIAS_SESION * 864e5);
  setCookie(c, "sid", token, {
    httpOnly: true, sameSite: "Lax", path: "/", maxAge: DIAS_SESION * 86400,
    secure: c.req.header("x-forwarded-proto") === "https",
  });
  return c.json({ usuario: u.usuario, nombre: u.nombre, rol: u.rol });
});

app.use("/api/*", async (c, next) => {
  const token = getCookie(c, "sid");
  const u = token && db.prepare(`SELECT u.id, u.usuario, u.nombre, u.rol FROM sesiones s JOIN usuarios u ON u.id = s.usuario_id
    WHERE s.token = ? AND s.expira > ?`).get(hashToken(token), Date.now()) as Usuario | undefined;
  if (!u) return c.json({ error: "Sesión no válida" }, 401);
  c.set("u", u);
  await next();
});
app.use("/api/admin/*", async (c, next) => {
  if (c.get("u").rol !== "admin") return c.json({ error: "Solo administradores" }, 403);
  await next();
});

app.post("/api/logout", c => {
  const token = getCookie(c, "sid");
  if (token) db.prepare("DELETE FROM sesiones WHERE token = ?").run(hashToken(token));
  deleteCookie(c, "sid", { path: "/" });
  return c.json({ ok: true });
});

app.get("/api/yo", c => c.json(c.get("u")));

app.get("/api/opciones", c => {
  const campos = Object.entries(NOMBRE_CAMPO).filter(([k]) => k !== "contentLanguage").map(([campo, nombre]) => ({ campo, nombre }));
  return c.json({ version: VERSION, fuente: meta.fuente, total_filas: +meta.total_filas, filas_llenadas: FILAS_LLENADAS,
    tarjetas_muestra: MUESTRA.length, campos, estratos: ESTRATOS, paises: PAISES });
});

app.get("/api/registros", c => {
  const u = c.get("u"), p = c.req.query(), admin = u.rol === "admin";
  const pagina = Math.max(0, parseInt(p.pagina ?? "0", 10) || 0);
  if (p.ambito === "completo") {
    if (!admin) return c.json({ error: "Solo administradores" }, 403);
    const { where, args, clave } = filtroCompleto(p, u.id);
    let total = clave ? cacheConteos.get(clave) : undefined;
    if (total === undefined) {
      total = (db.prepare(`SELECT COUNT(*) n FROM filas ${where}`).get(args) as { n: number }).n;
      if (clave) cacheConteos.set(clave, total);
    }
    const filas = db.prepare(`SELECT * FROM filas ${where} ORDER BY total_requests DESC, id LIMIT ${POR_PAGINA} OFFSET ${pagina * POR_PAGINA}`)
      .all(args) as Fila[];
    const regs = filas.map(f => MUESTRA_POR_FILA.get(f.id) ?? construirRegistro(f));
    return c.json({ total, pagina, por_pagina: POR_PAGINA, registros: conEtiquetas(regs, u.id, admin) });
  }
  const lista = filtrarMuestra(p, hechosMuestra(u.id));
  const regs = lista.slice(pagina * POR_PAGINA, (pagina + 1) * POR_PAGINA);
  return c.json({ total: lista.length, pagina, por_pagina: POR_PAGINA, registros: conEtiquetas(regs, u.id, admin) });
});

app.get("/api/progreso", c => {
  const u = c.get("u");
  const hechos = hechosMuestra(u.id);
  const muestra = {
    hechos: [...hechos].filter(k => ESTRATO_MUESTRA.has(k)).length, total: TOTAL_MUESTRA,
    tarjetas: MUESTRA.length, tarjetas_revisadas: MUESTRA.filter(r => pendientes(r, hechos) === 0).length,
  };
  if (u.rol !== "admin") return c.json({ muestra });
  const comp = db.prepare(`SELECT COUNT(*) etiquetas, COUNT(DISTINCT fila_id) filas FROM etiquetas
    WHERE usuario_id = ? AND substr(campo, 1, 1) <> '_'`).get(u.id);
  return c.json({ muestra, completo: { ...comp as object, filas_llenadas: FILAS_LLENADAS } });
});

app.get("/api/siguiente", c => {
  const hechos = hechosMuestra(c.get("u").id);
  return c.json({ posicion: MUESTRA.findIndex(r => pendientes(r, hechos) > 0) });
});

function puedeEditar(u: Usuario, filaId: number): Registro | null {
  const r = registroDe(filaId);
  if (!r || (u.rol !== "admin" && r.muestra_id === null)) return null;
  return r;
}

app.put("/api/etiquetas", async c => {
  const u = c.get("u");
  const b = await c.req.json().catch(() => null);
  if (!b) return c.json({ error: "JSON inválido" }, 400);
  const filaId = Number(b.fila_id), campo = String(b.campo ?? ""), valor = String(b.valor ?? "");
  const veredicto = String(b.veredicto ?? ""), correcto = String(b.valor_correcto ?? "").slice(0, 500);
  const r = puedeEditar(u, filaId);
  if (!r) return c.json({ error: "No tienes acceso a esta fila" }, 403);
  let valida: boolean;
  if (campo === FICHA) valida = r.extra?.imdb_id === valor;
  else if (campo.startsWith(ORIGINAL)) {
    const x = r.campos.find(k => k.campo === campo.slice(ORIGINAL.length));
    valida = !!x && !x.llenado && !!x.valor && x.valor === valor && (!veredicto || veredicto === "incorrecto");
  } else if (campo.startsWith(PREVIO)) {
    const x = r.campos.find(k => k.campo === campo.slice(PREVIO.length));
    valida = !!x && x.llenado && x.original === valor && (!veredicto || veredicto === "correcto");
  } else valida = llaves(r.campos).includes(`${campo}|${valor}`);
  if (!valida) return c.json({ error: "Ese valor no corresponde a la fila" }, 400);
  if (!veredicto) {
    db.prepare("DELETE FROM etiquetas WHERE usuario_id = ? AND fila_id = ? AND campo = ? AND valor = ?").run(u.id, filaId, campo, valor);
    return c.json({ ok: true, etiqueta: null });
  }
  if (!["correcto", "incorrecto", "no_se_sabe"].includes(veredicto)) return c.json({ error: "Veredicto inválido" }, 400);
  const ts = new Date().toISOString();
  db.prepare(`INSERT INTO etiquetas (usuario_id, fila_id, campo, valor, veredicto, valor_correcto, actualizado)
    VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (usuario_id, fila_id, campo, valor)
    DO UPDATE SET veredicto = excluded.veredicto, valor_correcto = excluded.valor_correcto, actualizado = excluded.actualizado`)
    .run(u.id, filaId, campo, valor, veredicto, correcto, ts);
  return c.json({ ok: true, etiqueta: { veredicto, correcto, ts } });
});

app.put("/api/notas", async c => {
  const u = c.get("u");
  const b = await c.req.json().catch(() => null);
  const filaId = Number(b?.fila_id), nota = String(b?.nota ?? "").slice(0, 2000);
  if (!puedeEditar(u, filaId)) return c.json({ error: "No tienes acceso a esta fila" }, 403);
  if (!nota.trim()) db.prepare("DELETE FROM notas WHERE usuario_id = ? AND fila_id = ?").run(u.id, filaId);
  else db.prepare(`INSERT INTO notas (usuario_id, fila_id, nota, actualizado) VALUES (?, ?, ?, ?)
    ON CONFLICT (usuario_id, fila_id) DO UPDATE SET nota = excluded.nota, actualizado = excluded.actualizado`)
    .run(u.id, filaId, nota, new Date().toISOString());
  return c.json({ ok: true });
});

// ---- Administración: avance, precisión y exportación compatible con calcular_precision_revision.py
app.get("/api/admin/resumen", c => {
  const usuarios = db.prepare("SELECT id, usuario, nombre, rol FROM usuarios ORDER BY id").all() as Usuario[];
  const todas = db.prepare("SELECT usuario_id, fila_id, campo, valor, veredicto, actualizado FROM etiquetas ORDER BY actualizado").all() as any[];
  const primero = new Map<string, string>(), porValor = new Map<string, string[]>();
  const salida = usuarios.map(u => {
    const mias = todas.filter(e => e.usuario_id === u.id);
    const enMuestra = mias.filter(e => MUESTRA_POR_FILA.has(e.fila_id));
    const ver = new Map(enMuestra.map(e => [`${e.fila_id}|${e.campo}|${e.valor}`, e.veredicto]));
    const hechos = new Set(ver.keys());
    return {
      ...u,
      muestra: {
        hechos: [...hechos].filter(k => ESTRATO_MUESTRA.has(k)).length, total: TOTAL_MUESTRA,
        tarjetas_revisadas: MUESTRA.filter(r => pendientes(r, hechos) === 0).length, tarjetas: MUESTRA.length,
      },
      completo: { etiquetas: mias.filter(e => !MUESTRA_POR_FILA.has(e.fila_id) && !e.campo.startsWith("_")).length },
      banderas: {
        original_mal: mias.filter(e => e.campo.startsWith(ORIGINAL)).length,
        previo_correcto: mias.filter(e => e.campo.startsWith(PREVIO)).length,
      },
      ultima: mias.at(-1)?.actualizado ?? null,
      precision: precision(ver),
    };
  });
  // Conjunto: el primer veredicto de cada valor, y el acuerdo donde hay dos o más revisores
  for (const e of todas) {
    if (!MUESTRA_POR_FILA.has(e.fila_id) || e.campo.startsWith(ORIGINAL) || e.campo.startsWith(PREVIO)) continue;
    const k = `${e.fila_id}|${e.campo}|${e.valor}`;
    if (!primero.has(k)) primero.set(k, e.veredicto);
    porValor.set(k, [...(porValor.get(k) ?? []), e.veredicto]);
  }
  const dobles = [...porValor.values()].filter(v => v.length >= 2);
  return c.json({
    usuarios: salida, conjunto: precision(primero),
    acuerdo: { valores: dobles.length, acuerdo: dobles.length ? dobles.filter(v => v[0] === v[1]).length / dobles.length : null },
  });
});

app.get("/api/admin/exportar", c => {
  const uid = Number(c.req.query("usuario")), ambito = c.req.query("ambito") ?? "muestra";
  const u = db.prepare("SELECT id, usuario, nombre FROM usuarios WHERE id = ?").get(uid) as Usuario | undefined;
  if (!u) return c.json({ error: "Usuario no encontrado" }, 404);
  const etq = new Map((db.prepare("SELECT * FROM etiquetas WHERE usuario_id = ?").all(uid) as any[])
    .map(e => [`${e.fila_id}|${e.campo}|${e.valor}`, e]));
  const notas = new Map((db.prepare("SELECT fila_id, nota FROM notas WHERE usuario_id = ?").all(uid) as any[]).map(x => [x.fila_id, x.nota]));
  const items: any[] = [];
  const item = (r: Registro, campo: string, valor: string, estrato: string, extra: object) => {
    const e = etq.get(`${r.fila_id}|${campo}|${valor}`);
    items.push({
      id: r.muestra_id ?? r.fila_id, fila_id: r.fila_id, titulo: r.titulo, app: r.app, publisher: r.publisher, pais: r.pais,
      requests: r.requests, campo, valor, estrato, ...extra, veredicto: e?.veredicto ?? "", valor_correcto: e?.valor_correcto ?? "",
      fecha: e?.actualizado ?? "", nota: notas.get(r.fila_id) ?? "",
    });
  };
  const registros = ambito === "completo"
    ? [...new Set([...etq.values()].map(e => e.fila_id))].filter(id => !MUESTRA_POR_FILA.has(id)).map(registroDe).filter(Boolean) as Registro[]
    : MUESTRA;
  for (const r of registros) {
    for (const c2 of r.campos.filter(x => x.llenado)) for (const un of c2.unidades) {
      if (ambito === "completo" && !etq.has(`${r.fila_id}|${c2.campo}|${un.valor}`)) continue;
      item(r, c2.campo, un.valor, un.estrato, { agregado: un.agregado, valor_campo: c2.valor, riesgo: c2.riesgo });
    }
    // banderas: solo las que el usuario marcó (no son parte de la muestra a juzgar)
    for (const c2 of r.campos) {
      const [campo, valor] = c2.llenado ? [PREVIO + c2.campo, c2.original] : [ORIGINAL + c2.campo, c2.valor];
      if (etq.has(`${r.fila_id}|${campo}|${valor}`)) item(r, campo, valor, campo.replace(":", "|"), { valor_campo: c2.valor });
    }
    if (r.extra && (ambito !== "completo" || etq.has(`${r.fila_id}|${FICHA}|${r.extra.imdb_id}`))) item(r, FICHA, r.extra.imdb_id, FICHA, {});
  }
  const version = ambito === "completo" ? `${VERSION}-completo` : VERSION;
  const salida = { version, revisor: u.nombre, exportado: new Date().toISOString(), totales_estrato: ambito === "completo" ? TOTALES : MUESTRA_META.totales_estrato, items };
  c.header("Content-Disposition", `attachment; filename="${version}-${u.usuario}-${new Date().toISOString().slice(0, 10)}.json"`);
  return c.json(salida);
});

// ---- Armador de deals (solo administradores)
rutasDeals(app, db);

app.all("/api/*", c => c.json({ error: "No encontrado" }, 404));

// ---- Front (Svelte compilado)
app.use("/*", serveStatic({ root: DIR_PUBLICO }));
const indice = (() => { try { return readFileSync(`${DIR_PUBLICO}/index.html`, "utf-8"); } catch { return "<p>Front no compilado</p>"; } })();
app.get("*", c => c.html(indice));

serve({ fetch: app.fetch, port: PUERTO }, () => console.log(`etiquetas-ctv escuchando en :${PUERTO} (${VERSION}, ${MUESTRA.length} en muestra)`));
