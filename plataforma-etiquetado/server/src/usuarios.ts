// Alta y cambio de clave de usuarios.
//   node dist/usuarios.js crear <usuario> <admin|revisor|deals> "<Nombre completo>" [clave]
//     deals = perfil que solo ve la pestaña Deals (se guarda como revisor con solo_deals = 1)
//   node dist/usuarios.js clave <usuario> [clave]
//   node dist/usuarios.js listar
// Sin clave se genera una aleatoria y se imprime una sola vez.
import { randomBytes } from "node:crypto";
import { abrir } from "./db.js";
import { hashClave } from "./auth.js";

const db = abrir();
const [cmd, usuario, ...resto] = process.argv.slice(2);
const generar = () => randomBytes(9).toString("base64url");

if (cmd === "crear" && usuario && ["admin", "revisor", "deals"].includes(resto[0]) && resto[1]) {
  const clave = resto[2] || generar(), deals = resto[0] === "deals";
  db.prepare("INSERT INTO usuarios (usuario, nombre, rol, solo_deals, clave) VALUES (?, ?, ?, ?, ?)")
    .run(usuario.toLowerCase(), resto[1], deals ? "revisor" : resto[0], deals ? 1 : 0, hashClave(clave));
  console.log(`Usuario ${usuario} (${resto[0]}) creado. Clave: ${clave}`);
} else if (cmd === "clave" && usuario) {
  const clave = resto[0] || generar();
  const r = db.prepare("UPDATE usuarios SET clave = ? WHERE usuario = ?").run(hashClave(clave), usuario);
  if (!r.changes) { console.error(`No existe el usuario ${usuario}`); process.exit(1); }
  db.prepare("DELETE FROM sesiones WHERE usuario_id = (SELECT id FROM usuarios WHERE usuario = ?)").run(usuario);
  console.log(`Clave de ${usuario} cambiada: ${clave}`);
} else if (cmd === "listar") {
  console.table(db.prepare("SELECT id, usuario, nombre, CASE WHEN solo_deals THEN 'deals' ELSE rol END AS rol, creado FROM usuarios").all());
} else {
  console.error('uso: usuarios.js crear <usuario> <admin|revisor|deals> "<Nombre>" [clave] | clave <usuario> [clave] | listar');
  process.exit(1);
}
