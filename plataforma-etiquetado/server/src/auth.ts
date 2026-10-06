import { createHash, randomBytes, scryptSync, timingSafeEqual } from "node:crypto";

export function hashClave(clave: string): string {
  const sal = randomBytes(16);
  return `scrypt$${sal.toString("hex")}$${scryptSync(clave, sal, 64).toString("hex")}`;
}

export function verificarClave(clave: string, guardada: string): boolean {
  const [alg, sal, hash] = guardada.split("$");
  if (alg !== "scrypt" || !sal || !hash) return false;
  const calc = scryptSync(clave, Buffer.from(sal, "hex"), 64);
  const esperado = Buffer.from(hash, "hex");
  return calc.length === esperado.length && timingSafeEqual(calc, esperado);
}

export const nuevoToken = () => randomBytes(32).toString("base64url");
// En la base solo se guarda el hash del token: una copia de la base no da sesiones válidas
export const hashToken = (t: string) => createHash("sha256").update(t).digest("hex");
