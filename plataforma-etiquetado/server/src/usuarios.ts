// Alta y cambio de clave de usuarios.
//   node dist/usuarios.js crear <usuario> <admin|revisor> "<Nombre completo>" [clave]
//   node dist/usuarios.js clave <usuario> [clave]
//   node dist/usuarios.js listar
// Sin clave se genera una aleatoria y se imprime una sola vez.
import { randomBytes } from "node:crypto";
import { abrir } from "./db.js";
import { hashClave } from "./auth.js";

const db = abrir();
const [cmd, usuario, ...resto] = process.argv.slice(2);
const generar = () => randomBytes(9).toString("base64url");

if (cmd === "crear" && usuario && ["admin", "revisor"].includes(resto[0]) && resto[1]) {
  const clave = resto[2] || generar();
  db.prepare("INSERT INTO usuarios (usuario, nombre, rol, clave) VALUES (?, ?, ?, ?)").run(usuario, resto[1], resto[0], hashClave(clave));
  console.log(`Usuario ${usuario} (${resto[0]}) creado. Clave: ${clave}`);
} else if (cmd === "clave" && usuario) {
  const clave = resto[0] || generar();
  const r = db.prepare("UPDATE usuarios SET clave = ? WHERE usuario = ?").run(hashClave(clave), usuario);
  if (!r.changes) { console.error(`No existe el usuario ${usuario}`); process.exit(1); }
  db.prepare("DELETE FROM sesiones WHERE usuario_id = (SELECT id FROM usuarios WHERE usuario = ?)").run(usuario);
  console.log(`Clave de ${usuario} cambiada: ${clave}`);
} else if (cmd === "listar") {
  console.table(db.prepare("SELECT id, usuario, nombre, rol, creado FROM usuarios").all());
} else {
  console.error('uso: usuarios.js crear <usuario> <admin|revisor> "<Nombre>" [clave] | clave <usuario> [clave] | listar');
  process.exit(1);
}
