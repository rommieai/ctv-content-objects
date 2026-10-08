import Database from "better-sqlite3";

export const RUTA_DB = process.env.DB_PATH ?? "/data/etiquetas.db";
export const DIR_IAB = process.env.IAB_DIR ?? new URL("../iab", import.meta.url).pathname;

// Tablas de la plataforma. Las de datos (filas, muestra, meta) las crea importar.ts y se pueden
// reimportar sin tocar usuarios ni etiquetas: fila_id es la posición de la fila en el CSV.
const ESQUEMA = `
CREATE TABLE IF NOT EXISTS usuarios (
  id INTEGER PRIMARY KEY,
  usuario TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  rol TEXT NOT NULL CHECK (rol IN ('admin', 'revisor')),
  solo_deals INTEGER NOT NULL DEFAULT 0,
  clave TEXT NOT NULL,
  creado TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS sesiones (
  token TEXT PRIMARY KEY,
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  expira INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS etiquetas (
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  fila_id INTEGER NOT NULL,
  campo TEXT NOT NULL,
  valor TEXT NOT NULL,
  veredicto TEXT NOT NULL CHECK (veredicto IN ('correcto', 'incorrecto', 'no_se_sabe')),
  valor_correcto TEXT NOT NULL DEFAULT '',
  actualizado TEXT NOT NULL,
  PRIMARY KEY (usuario_id, fila_id, campo, valor)
);
CREATE INDEX IF NOT EXISTS idx_etiquetas_fila ON etiquetas(fila_id);
CREATE TABLE IF NOT EXISTS notas (
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  fila_id INTEGER NOT NULL,
  nota TEXT NOT NULL,
  actualizado TEXT NOT NULL,
  PRIMARY KEY (usuario_id, fila_id)
);
`;

export function abrir(ruta = RUTA_DB) {
  const db = new Database(ruta);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  db.exec(ESQUEMA);
  // Perfil que solo ve la pestaña Deals. Va en una columna aparte y no como un rol más porque cambiar el
  // CHECK de rol obligaría a recrear usuarios, y de esa tabla cuelgan las etiquetas (ON DELETE CASCADE).
  if (!(db.pragma("table_info(usuarios)") as { name: string }[]).some(c => c.name === "solo_deals")) {
    db.exec("ALTER TABLE usuarios ADD COLUMN solo_deals INTEGER NOT NULL DEFAULT 0");
  }
  return db;
}
