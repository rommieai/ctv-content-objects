// Traducciones y significados de los códigos que se muestran al revisor.
// Port de scripts/generar_muestra_revision.py (mismas tablas, mismo criterio).
import { readFileSync } from "node:fs";
import { join } from "node:path";

export const IAB_ES: Record<string, string> = {
  "Arts & Entertainment": "Arte y entretenimiento", "Movies": "Películas", "Television": "Televisión",
  "Music": "Música", "Sports": "Deportes", "News": "Noticias", "Food & Drink": "Comida y bebida",
  "Travel": "Viajes", "Religion & Spirituality": "Religión y espiritualidad", "Education": "Educación",
  "Video & Computer Games": "Videojuegos", "Family & Parenting": "Familia y crianza", "Humor": "Humor",
  "Hobbies & Interests": "Pasatiempos", "Science": "Ciencia", "Technology & Computing": "Tecnología",
  "Business": "Negocios", "Health & Fitness": "Salud y ejercicio", "Home & Garden": "Hogar y jardín",
  "Style & Fashion": "Moda y estilo", "Automotive": "Automotriz", "Pets": "Mascotas",
  "Society": "Sociedad", "Law, Gov't & Politics": "Leyes, gobierno y política", "Real Estate": "Bienes raíces",
  "Personal Finance": "Finanzas personales", "Careers": "Empleo", "Shopping": "Compras",
  "Uncategorized": "Sin categoría", "Fine Art": "Bellas artes", "Celebrity Fan/Gossip": "Celebridades",
  "Books & Literature": "Libros y literatura", "Humor ": "Humor", "Documentary": "Documental",
  "Action and Adventure Movies": "Películas de acción y aventura", "Comedy Movies": "Películas de comedia",
  "Drama Movies": "Películas de drama", "Horror Movies": "Películas de terror",
  "Romance Movies": "Películas románticas", "Science Fiction Movies": "Películas de ciencia ficción",
  "Family and Children Movies": "Películas familiares e infantiles", "Documentary Movies": "Películas documentales",
  "Crime and Mystery Movies": "Películas de crimen y misterio", "Animation Movies": "Películas animadas",
  "Fantasy Movies": "Películas de fantasía", "Western Movies": "Películas del oeste", "World Movies": "Cine del mundo",
  "Action TV": "Series de acción", "Comedy TV": "Series de comedia", "Drama TV": "Series de drama",
  "Reality TV": "Reality", "Children's TV": "TV infantil", "Animation TV": "Series animadas",
  "Crime TV": "Series policiales", "Documentary TV": "TV documental", "Science Fiction TV": "Series de ciencia ficción",
  "Soap Opera TV": "Telenovelas", "Special Interest TV": "TV de interés especial", "Sports TV": "TV deportiva",
  "Family/Children TV": "TV familiar / infantil", "Mystery TV": "Series de misterio", "Fantasy TV": "Series de fantasía",
  "Horror TV": "Series de terror", "Music TV": "TV musical", "Talk Show": "Programa de entrevistas",
  "Game Show": "Concursos", "Holiday TV": "TV de temporada / fiestas", "Romance TV": "Series románticas",
  "Science Fiction": "Ciencia ficción", "Soccer": "Fútbol", "Boxing": "Boxeo", "Wrestling": "Lucha libre",
  "Auto Racing": "Automovilismo", "Basketball": "Baloncesto", "Baseball": "Béisbol",
  "American Football": "Fútbol americano", "Tennis": "Tenis", "Mixed Martial Arts": "Artes marciales mixtas",
  "Golf": "Golf", "Cooking": "Cocina", "Video Gaming": "Videojuegos", "Entertainment": "Entretenimiento",
  "Pop Culture": "Cultura pop", "Comics and Animation": "Cómics y animación", "Anime": "Anime",
  "International News": "Noticias internacionales", "Local News": "Noticias locales",
  "National News": "Noticias nacionales", "Weather": "Clima", "Politics": "Política",
};

export const RATING_SIGNIFICADO: Record<string, string> = {
  "g": "Apto para todo público (escala de EE. UU.)", "pg": "Se sugiere supervisión de los padres (EE. UU.)",
  "pg-13": "Mayores de 13 años (EE. UU.)", "r": "Mayores de 17, o menores acompañados (EE. UU.)",
  "nc-17": "Solo adultos, 18+ (EE. UU.)", "tv-y": "Infantil, todas las edades (TV EE. UU.)",
  "tv-y7": "Niños de 7 años o más (TV EE. UU.)", "tv-g": "Todo público (TV EE. UU.)",
  "tv-pg": "Supervisión de los padres, aprox. 10+ (TV EE. UU.)", "tv-14": "Mayores de 14 años (TV EE. UU.)",
  "tv-ma": "Solo adultos, 17+ (TV EE. UU.)", "nr": "Sin clasificar", "unrated": "Sin clasificar",
  "not rated": "Sin clasificar", "all ages": "Todas las edades (escala nueva del reporte, equivale a G)",
  "teen": "Adolescentes, aprox. 10+ (escala nueva del reporte, equivale a TV-PG)",
  "teen plus": "Mayores de 13–15 (escala nueva del reporte, equivale a TV-14)",
  "adults": "Solo adultos, 18+ (escala nueva del reporte, equivale a R / TV-MA)",
  "aa": "Infantil (clasificación RTC de México)", "a": "Todo público (clasificación RTC de México)",
  "b": "Adolescentes de 12 años o más (clasificación RTC de México)",
  "b15": "Mayores de 15 años (clasificación RTC de México)", "c": "Mayores de 18 años (clasificación RTC de México)",
  "d": "Solo adultos, contenido explícito (clasificación RTC de México)",
  "tp": "Todos los públicos (escala de España)", "bbfc-pg": "Supervisión de los padres (escala británica BBFC)",
  "bbfc-u": "Todo público (escala británica BBFC)", "bbfc-12": "Mayores de 12 (escala británica BBFC)",
  "bbfc-15": "Mayores de 15 (escala británica BBFC)", "bbfc-18": "Solo adultos (escala británica BBFC)",
  "l": "Libre, todas las edades (escala de Brasil)", "atp": "Apta para todo público (escala de Argentina)",
};

const IAB_NO_ESTANDAR: Record<string, string> = {
  "IAB1-22": "Código no estándar (no existe en IAB 1.0); varios vendedores lo usan para «Entretenimiento» en general",
};
const LIVESTREAM: Record<string, string> = {
  "1": "Sí: en vivo o canal lineal (programado en horario)", "0": "No: bajo demanda (el usuario elige qué ver)",
};
export const TIPO_ES: Record<string, string> = {
  movie: "película", tvSeries: "serie", tvMiniSeries: "miniserie", tvMovie: "película para TV",
  short: "cortometraje", video: "video", tvSpecial: "especial de TV", tvShort: "corto de TV",
};

export interface Iab { codigo: string; es: string; en: string; tax: string }
export type Significado = { iab: Iab[] } | { texto: string } | null;

// codigo -> ruta en inglés. 1.0 por código IABx-y; 2.2/3.0 por id numérico.
const iab10 = new Map<string, string[]>();
const iab2 = new Map<string, { "2.2"?: string[]; "3.0"?: string[] }>();

export function cargarIab(dir: string) {
  const filas = (f: string) => readFileSync(join(dir, f), "utf-8").split(/\r?\n/).map(l => l.split("\t"));
  const padres = new Map<string, string>();
  for (const row of filas("Content_Taxonomy_1.0.tsv").slice(1)) {
    if (row.length < 3) continue;
    const cod = row[0].trim(), nombre = row[2].trim();
    padres.set(cod, nombre);
    iab10.set(cod, cod.includes("-") ? [padres.get(cod.split("-")[0]) ?? "", nombre] : [nombre]);
  }
  for (const v of ["2.2", "3.0"] as const) {
    for (const row of filas(`Content_Taxonomy_${v}.tsv`).slice(2)) {
      if (row.length < 4 || !row[0].trim()) continue;
      const ruta = row.slice(3, 7).map(x => x.trim()).filter(Boolean);
      const id = row[0].trim();
      iab2.set(id, { ...iab2.get(id), [v]: ruta });
    }
  }
}

const esRuta = (ruta: string[]) => ruta.map(x => IAB_ES[x] ?? x).join(" › ");

export function significadoCategoria(valor: string): Iab[] {
  const out: Iab[] = [];
  const codigos = valor.trim().replace(/^[\[\]]+|[\[\]]+$/g, "").split(",").map(x => x.trim()).filter(Boolean);
  for (const c of codigos) {
    const up = c.toUpperCase();
    const t = iab2.get(c);
    if (up.startsWith("IAB") && iab10.has(up)) {
      const ruta = iab10.get(up)!;
      out.push({ codigo: c, es: esRuta(ruta), en: ruta.join(" › "), tax: "IAB 1.0" });
    } else if (t) {
      const ruta = (t["2.2"] ?? t["3.0"])!;
      let nota = t["2.2"] ? "IAB 2.2" : "IAB 3.0";
      if (t["2.2"] && t["3.0"] && t["2.2"].join("|") !== t["3.0"].join("|")) nota = `IAB 2.2 (en 3.0: ${t["3.0"].join(" › ")})`;
      out.push({ codigo: c, es: esRuta(ruta), en: ruta.join(" › "), tax: nota });
    } else if (IAB_NO_ESTANDAR[up]) {
      out.push({ codigo: c, es: IAB_NO_ESTANDAR[up], en: "", tax: "" });
    } else if (!/\d/.test(c)) {
      out.push({ codigo: c, es: "texto libre del vendedor, no es un código IAB", en: "", tax: "" });
    } else {
      out.push({ codigo: c, es: "código que no existe en las taxonomías IAB (1.0, 2.2, 3.0)", en: "", tax: "" });
    }
  }
  return out;
}

export function significado(campo: string, valor: string, runtime: string): Significado {
  const v = (valor ?? "").trim();
  if (!v) return null;
  if (campo === "contentCategory") return { iab: significadoCategoria(v) };
  if (campo === "contentRating") {
    let t = RATING_SIGNIFICADO[v.toLowerCase()] ?? "";
    const num = v.replace(/^[+\- ]+|[+\- ]+$/g, "");
    if (!t && /^\d+$/.test(num)) t = +num > 0 ? `Mayores de ${+num} años` : "Todas las edades";
    return { texto: t };
  }
  if (campo === "contentIsLiveStream") return { texto: LIVESTREAM[v] ?? "" };
  if (campo === "contentLength") {
    let t = "Código del reporte (1 a 8); PubMatic no ha confirmado a qué duración corresponde cada código.";
    if (runtime) t += ` Según IMDb/Wikidata la obra dura ${runtime} min.`;
    return { texto: t };
  }
  return null;
}
