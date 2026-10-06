// Carga el consolidado relleno completo y la muestra de revisión a SQLite.
//
//   node dist/importar.js <inventory-consolidado-...-relleno.csv> <revision-manual-v22.json>
//
// Reemplaza las tablas de datos (filas, muestra, meta) y deja intactos usuarios, sesiones, etiquetas
// y notas. Las etiquetas apuntan a fila_id = posición de la fila en el CSV (1..N), así que reimportar
// el MISMO CSV conserva todo lo etiquetado.
import { createReadStream, readFileSync } from "node:fs";
import { parse } from "csv-parse";
import { abrir, DIR_IAB } from "./db.js";
import { cargarIab } from "./significados.js";
import { construirCampos, construirRegistro, llaves, tituloLegible, usaExterno, type Fila } from "./registros.js";

const [rutaCsv, rutaMuestra] = process.argv.slice(2);
if (!rutaCsv || !rutaMuestra) {
  console.error("uso: node dist/importar.js <consolidado-relleno.csv> <revision-manual.json>");
  process.exit(1);
}

// Encabezados del CSV con espacios o mayúsculas -> nombre de columna; el resto se queda igual
const RENOMBRE: Record<string, string> = {
  "Publisher ID": "publisher_id", "Publisher": "publisher", "pageURL": "page_url", "App Name": "app_name",
  "Country": "country", "Total Requests": "total_requests", "eCPM": "ecpm",
};
const col = (h: string) => RENOMBRE[h] ?? h;

cargarIab(DIR_IAB);
const db = abrir();
db.pragma("synchronous = OFF");
db.exec(`DROP TABLE IF EXISTS muestra; DROP TABLE IF EXISTS filas; DROP TABLE IF EXISTS meta;
  CREATE TABLE meta (clave TEXT PRIMARY KEY, valor TEXT NOT NULL);`);

const t0 = Date.now();
const parser = createReadStream(rutaCsv).pipe(parse({ bom: true, relax_column_count: true }));
let encabezado: string[] = [];
let insertar: ReturnType<typeof db.prepare> | null = null;
let lote: any[][] = [];
let n = 0;
const totales: Record<string, { filas: number; requests: number }> = {};
const insertarLote = db.transaction((filas: any[][]) => { for (const f of filas) insertar!.run(f); });

for await (const row of parser as AsyncIterable<string[]>) {
  if (!encabezado.length) {
    encabezado = row.map(col);
    for (const req of ["contentTitle", "total_requests", "contentCategory_relleno", "contentCategory_origen", "ext_imdb_id"]) {
      if (!encabezado.includes(req)) throw new Error(`El CSV no trae la columna ${req}`);
    }
    const defs = encabezado.map(h => `"${h}" ${h === "total_requests" ? "INTEGER" : h === "ecpm" ? "REAL" : "TEXT"}`);
    db.exec(`CREATE TABLE filas (id INTEGER PRIMARY KEY, ${defs.join(", ")},
      titulo TEXT NOT NULL, n_unidades INTEGER NOT NULL, en_muestra INTEGER NOT NULL DEFAULT 0, muestra_id INTEGER)`);
    const cols = [...encabezado, "id", "titulo", "n_unidades"];
    insertar = db.prepare(`INSERT INTO filas (${cols.map(c => `"${c}"`).join(", ")}) VALUES (${cols.map(() => "?").join(", ")})`);
    continue;
  }
  n++;
  const f: Fila = {};
  encabezado.forEach((h, i) => { f[h] = row[i] ?? ""; });
  f.total_requests = parseInt(f.total_requests || "0", 10) || 0;
  f.ecpm = f.ecpm === "" ? null : Number(f.ecpm);
  const campos = construirCampos(f);
  for (const c of campos) {
    if (!c.llenado) continue;
    const e = `${c.campo}|${f[c.campo + "_origen"]}`;
    (totales[e] ??= { filas: 0, requests: 0 }).filas++;
    totales[e].requests += f.total_requests;
  }
  if (f.contentCategory_afinado_origen) {
    const e = `contentCategory_afinado|${f.contentCategory_afinado_origen}`;
    (totales[e] ??= { filas: 0, requests: 0 }).filas++;
    totales[e].requests += f.total_requests;
  }
  lote.push([...encabezado.map(h => f[h]), n, tituloLegible(f.contentTitle), llaves(campos).length]);
  if (lote.length === 20000) {
    insertarLote(lote);
    lote = [];
    process.stdout.write(`\r${n.toLocaleString("es-MX")} filas`);
  }
}
insertarLote(lote);
console.log(`\r${n.toLocaleString("es-MX")} filas cargadas en ${((Date.now() - t0) / 1000).toFixed(0)} s`);

console.log("Creando índices…");
db.exec(`
  CREATE INDEX idx_filas_requests ON filas(total_requests DESC);
  CREATE INDEX idx_filas_muestra ON filas(muestra_id) WHERE muestra_id IS NOT NULL;
  CREATE INDEX idx_filas_pais ON filas(country, total_requests DESC);
  CREATE INDEX idx_filas_llenadas ON filas(total_requests DESC) WHERE n_unidades > 0;
`);

// ---- Muestra: cada registro del JSON de revisión se ubica en su fila del CSV
const muestra = JSON.parse(readFileSync(rutaMuestra, "utf-8"));
db.exec(`CREATE TABLE muestra (id INTEGER PRIMARY KEY, fila_id INTEGER NOT NULL UNIQUE, campos TEXT NOT NULL,
  extra TEXT, ayuda TEXT NOT NULL)`);
const candidatas = db.prepare(`SELECT * FROM filas WHERE total_requests = ? AND app_name = ? AND page_url = ?
  AND publisher = ? AND country = ?`);
const insMuestra = db.prepare("INSERT INTO muestra (id, fila_id, campos, extra, ayuda) VALUES (?, ?, ?, ?, ?)");
const marcar = db.prepare("UPDATE filas SET en_muestra = 1, muestra_id = ? WHERE id = ?");
let sinFila = 0, distintas = 0;
db.transaction(() => {
  for (const r of muestra.registros) {
    const esperadas = llaves(r.campos).sort().join("\n");
    const cands = (candidatas.all(r.requests, r.app, r.bundle, r.publisher, r.pais) as Fila[]).filter(f => f.titulo === r.titulo);
    const f = cands.find(x => llaves(construirCampos(x)).sort().join("\n") === esperadas) ?? cands[0];
    if (!f) { sinFila++; console.warn(`  muestra #${r.id} "${r.titulo}" no aparece en el CSV`); continue; }
    if (llaves(construirRegistro(f).campos).sort().join("\n") !== esperadas || !!r.extra !== (usaExterno(f) && !!f.ext_imdb_id)) {
      distintas++;
      console.warn(`  muestra #${r.id} "${r.titulo}": las unidades recalculadas no coinciden con el JSON`);
    }
    insMuestra.run(r.id, f.id, JSON.stringify(r.campos), r.extra ? JSON.stringify(r.extra) : null, JSON.stringify(r.ayuda));
    marcar.run(r.id, f.id);
  }
})();
console.log(`Muestra: ${muestra.registros.length - sinFila} de ${muestra.registros.length} registros ubicados` +
  (distintas ? ` (${distintas} con unidades distintas)` : ""));

const setMeta = db.prepare("INSERT INTO meta (clave, valor) VALUES (?, ?)");
setMeta.run("version", muestra.meta.version);
setMeta.run("fuente", rutaCsv.split("/").pop()!);
setMeta.run("muestra_meta", JSON.stringify(muestra.meta));
setMeta.run("totales_estrato", JSON.stringify(totales));
setMeta.run("total_filas", String(n));
setMeta.run("columnas", JSON.stringify(encabezado));
setMeta.run("paises", JSON.stringify((db.prepare("SELECT country, COUNT(*) n FROM filas GROUP BY country ORDER BY n DESC").all() as any[]).map(x => x.country)));
db.exec("ANALYZE");
db.close();
console.log(`Listo en ${((Date.now() - t0) / 1000).toFixed(0)} s`);
