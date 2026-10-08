// AI Deals: lee el brief de una campaña y elige los content objects con los que se arma el deal.
//
// Claude recibe el brief y el catálogo de lo que hay en el corte vigente (países, géneros, categorías,
// clasificaciones e idiomas, con su peso en requests) y devuelve un plan con valores de ese catálogo. La salida
// es estructurada: el esquema solo admite valores que existen, así que el plan siempre se puede simular y crear.
import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { z } from "zod";

const MODELO = process.env.AI_DEALS_MODELO ?? "claude-opus-5-5";
export const aiConfigurado = () => !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);

export interface ValorCatalogo { valor: string; nombre?: string; pct: number }
export interface Catalogo {
  paises: ValorCatalogo[]; generos: ValorCatalogo[]; categorias: ValorCatalogo[]; ratings: ValorCatalogo[]; idiomas: ValorCatalogo[];
}
export interface PlanBrief {
  paises: string[]; generos: string[]; categorias: string[]; ratings: string[]; idioma: string;
  palabras_clave: string[]; razon: string;
}
export class ErrorAi extends Error {}

const SIN_IDIOMA = "(cualquiera)";
const MAX = { paises: 12, generos: 4, categorias: 2, ratings: 3, palabras_clave: 4 };

const SISTEMA = `Eres planner de medios de una empresa que vende publicidad en televisión conectada (CTV) en Latinoamérica.
Recibes el brief de una campaña y el catálogo del inventario disponible, y eliges con qué content objects se arma el deal.

Cómo se usa lo que elijas:
- Dentro de un mismo content object, varios valores se suman (cualquiera de ellos entra).
- Entre content objects distintos, las condiciones se cruzan (deben cumplirse todas). Cada content object que agregas reduce el alcance.

Criterio:
- El género es el criterio principal: elige de 1 a ${MAX.generos} géneros que de verdad encajen con la marca, el producto y el público del brief. No rellenes con géneros genéricos solo por volumen.
- Categoría IAB: úsala solo si el brief pide explícitamente un tipo de contenido (películas, series o televisión, deportes, noticias…). Si no, déjala vacía.
- Clasificación (rating): úsala solo si el brief lo exige por público o por seguridad de marca (por ejemplo, contenido infantil o exclusión de contenido para adultos). Si no, déjala vacía.
- Idioma: elígelo solo si el brief pide un idioma de forma explícita. Si no, "${SIN_IDIOMA}".
- Países: los que mencione el brief. Si habla de una región, los países del catálogo que pertenezcan a ella. Si no menciona ninguno, todos los del catálogo.
- palabras_clave: de 2 a ${MAX.palabras_clave} palabras cortas, en minúsculas y sin acentos, que identifiquen la campaña (marca o producto, tema, mercado). Sirven para nombrar el deal.
- razon: dos o tres frases en español, para quien arma el deal, explicando por qué esos content objects responden al brief. Sin tecnicismos.

Usa únicamente valores del catálogo. El porcentaje junto a cada valor es su peso en los requests del inventario: sirve para no elegir algo sin volumen, no para elegir lo más grande.`;

const lista = (titulo: string, vs: ValorCatalogo[]) =>
  `${titulo}:\n` + vs.map(v => `- ${v.valor}${v.nombre ? ` (${v.nombre})` : ""} · ${v.pct.toFixed(1)}%`).join("\n");

const enumDe = (vs: string[]) => z.enum(vs as [string, ...string[]]);
const slug = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

/** Pide a Claude el plan de content objects para un brief. Lanza ErrorAi con un mensaje para mostrar en pantalla. */
export async function interpretarBrief(brief: string, cat: Catalogo): Promise<PlanBrief> {
  const Plan = z.object({
    paises: z.array(enumDe(cat.paises.map(x => x.valor))),
    generos: z.array(enumDe(cat.generos.map(x => x.valor))),
    categorias: z.array(enumDe(cat.categorias.map(x => x.valor))),
    ratings: z.array(enumDe(cat.ratings.map(x => x.valor))),
    idioma: enumDe([SIN_IDIOMA, ...cat.idiomas.map(x => x.valor)]),
    palabras_clave: z.array(z.string()),
    razon: z.string(),
  });
  const catalogo = [
    lista("Países", cat.paises), lista("Géneros", cat.generos), lista("Categorías IAB", cat.categorias),
    lista("Clasificaciones", cat.ratings), lista("Idiomas", cat.idiomas),
  ].join("\n\n");

  const client = new Anthropic();
  let respuesta;
  try {
    respuesta = await client.messages.parse({
      model: MODELO,
      max_tokens: 16000,
      thinking: { type: "adaptive" },
      output_config: { effort: "medium", format: zodOutputFormat(Plan) },
      system: SISTEMA,
      messages: [{ role: "user", content: `<catalogo>\n${catalogo}\n</catalogo>\n\n<brief>\n${brief}\n</brief>` }],
    });
  } catch (e) {
    if (e instanceof Anthropic.AuthenticationError) throw new ErrorAi("La llave de la API de Anthropic no es válida");
    if (e instanceof Anthropic.RateLimitError) throw new ErrorAi("La API de Anthropic está limitando las solicitudes; intenta de nuevo en un momento");
    if (e instanceof Anthropic.APIConnectionError) throw new ErrorAi("No se pudo conectar con la API de Anthropic");
    if (e instanceof Anthropic.APIError) throw new ErrorAi(`La API de Anthropic respondió con error ${e.status ?? ""}`.trim());
    throw e;
  }
  if (respuesta.stop_reason === "refusal") throw new ErrorAi("El modelo no quiso procesar ese brief. Revisa el texto e intenta de nuevo");
  const p = respuesta.parsed_output;
  if (!p) throw new ErrorAi("El modelo no devolvió un plan que se pudiera leer. Intenta de nuevo");

  const unicos = <T>(xs: T[], n: number) => [...new Set(xs)].slice(0, n);
  const paises = unicos(p.paises, MAX.paises);
  return {
    paises: paises.length ? paises : cat.paises.slice(0, MAX.paises).map(x => x.valor),
    generos: unicos(p.generos, MAX.generos),
    categorias: unicos(p.categorias, MAX.categorias),
    ratings: unicos(p.ratings, MAX.ratings),
    idioma: p.idioma === SIN_IDIOMA ? "" : p.idioma,
    palabras_clave: unicos(p.palabras_clave.map(slug).filter(Boolean), MAX.palabras_clave),
    razon: p.razon.trim().slice(0, 900),
  };
}
