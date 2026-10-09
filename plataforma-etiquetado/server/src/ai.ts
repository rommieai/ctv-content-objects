// AI Deals: lee el brief de una campaña y elige los content objects con los que se arma el deal.
//
// El modelo recibe el brief y el catálogo de lo que hay en el corte vigente para el mercado (país) que eligió la
// persona (géneros, categorías, clasificaciones e idiomas, con su peso en requests) y devuelve un plan con valores de ese catálogo. La salida
// es estructurada: el esquema solo admite valores que existen, así que el plan siempre se puede simular y crear.
//
// Dos proveedores: Claude (ANTHROPIC_API_KEY) o un modelo abierto servido por Groq (GROQ_API_KEY, tiene capa
// gratuita). Si están las dos llaves manda Claude, salvo que AI_DEALS_PROVEEDOR diga otra cosa.
import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { z } from "zod";

const HAY_ANTHROPIC = !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);
// con la llave de respaldo se sigue cuando la principal se queda sin cupo
const LLAVES_GROQ = [process.env.GROQ_API_KEY, process.env.GROQ_API_KEY_BACKUP].filter((x): x is string => !!x);
const PROVEEDOR = process.env.AI_DEALS_PROVEEDOR === "groq" || process.env.AI_DEALS_PROVEEDOR === "anthropic"
  ? process.env.AI_DEALS_PROVEEDOR : HAY_ANTHROPIC || !LLAVES_GROQ.length ? "anthropic" : "groq";
const MODELO = process.env.AI_DEALS_MODELO ?? (PROVEEDOR === "groq" ? "openai/gpt-oss-120b" : "claude-opus-5-5");
const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
export const aiConfigurado = () => (PROVEEDOR === "groq" ? LLAVES_GROQ.length > 0 : HAY_ANTHROPIC);

export interface ValorCatalogo { valor: string; nombre?: string; pct: number }
export interface Catalogo {
  generos: ValorCatalogo[]; categorias: ValorCatalogo[]; ratings: ValorCatalogo[]; idiomas: ValorCatalogo[];
}
export interface PlanBrief {
  paises: string[]; generos: string[]; categorias: string[]; ratings: string[]; idioma: string;
  palabras_clave: string[]; razon: string;
}
export class ErrorAi extends Error {}

const SIN_IDIOMA = "(cualquiera)";
const MAX = { generos: 4, categorias: 2, ratings: 3, palabras_clave: 4 };

const SISTEMA = `Eres planner de medios de una empresa que vende publicidad en televisión conectada (CTV) en Latinoamérica.
Recibes el brief de una campaña, el mercado (país) donde va a correr y el catálogo del inventario disponible en ese mercado, y eliges con qué content objects se arma el deal.

Cómo se usa lo que elijas:
- Dentro de un mismo content object, varios valores se suman (cualquiera de ellos entra).
- Entre content objects distintos, las condiciones se cruzan (deben cumplirse todas). Cada content object que agregas reduce el alcance.

Criterio:
- El género es el criterio principal: elige de 1 a ${MAX.generos} géneros que de verdad encajen con la marca, el producto y el público del brief. No rellenes con géneros genéricos solo por volumen.
- Categoría IAB: úsala solo si el brief pide explícitamente un tipo de contenido (películas, series o televisión, deportes, noticias…). Si no, déjala vacía.
- Clasificación (rating): úsala solo si el brief lo exige por público o por seguridad de marca (por ejemplo, contenido infantil o exclusión de contenido para adultos). Si no, déjala vacía.
- Idioma: elígelo solo si el brief pide un idioma de forma explícita. Si no, "${SIN_IDIOMA}".
- El mercado ya está decidido: no lo elijas ni lo cambies aunque el brief mencione otros países.
- palabras_clave: de 2 a ${MAX.palabras_clave} palabras cortas, en minúsculas y sin acentos, que identifiquen la campaña (marca o producto, tema). Sirven para nombrar el deal.
- razon: dos o tres frases en español, para quien arma el deal, explicando por qué esos content objects responden al brief. Sin tecnicismos.

Usa únicamente valores del catálogo. El porcentaje junto a cada valor es su peso en los requests del inventario: sirve para no elegir algo sin volumen, no para elegir lo más grande.`;

const lista = (titulo: string, vs: ValorCatalogo[]) =>
  `${titulo}:\n` + vs.map(v => `- ${v.valor}${v.nombre ? ` (${v.nombre})` : ""} · ${v.pct.toFixed(1)}%`).join("\n");

const enumDe = (vs: string[]) => z.enum(vs as [string, ...string[]]);
const slug = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

/** El plan con Groq (API compatible con OpenAI): salida JSON atada al esquema. Devuelve lo que mandó el modelo, sin validar. */
async function pedirAGroq(usuario: string, esquema: unknown): Promise<unknown> {
  for (const [i, llave] of LLAVES_GROQ.entries()) {
    let r: Response;
    try {
      r = await fetch(GROQ_URL, {
        method: "POST", headers: { Authorization: `Bearer ${llave}`, "Content-Type": "application/json" }, signal: AbortSignal.timeout(90_000),
        body: JSON.stringify({
          model: MODELO, temperature: 0.2, max_completion_tokens: 3000,
          response_format: { type: "json_schema", json_schema: { name: "plan", strict: true, schema: esquema } },
          messages: [{ role: "system", content: SISTEMA }, { role: "user", content: usuario }],
        }),
      });
    } catch { throw new ErrorAi("No se pudo conectar con la API de Groq"); }
    if (r.ok) {
      const j = await r.json().catch(() => null) as { choices?: { message?: { content?: string } }[] } | null;
      try { return JSON.parse(j?.choices?.[0]?.message?.content ?? ""); } catch { return null; }
    }
    const sinCupo = r.status === 401 || r.status === 403 || r.status === 429;
    if (sinCupo && i < LLAVES_GROQ.length - 1) continue;
    console.error(`ai deals (groq ${r.status}):`, (await r.text().catch(() => "")).slice(0, 300));
    if (r.status === 401 || r.status === 403) throw new ErrorAi("La llave de la API de Groq no es válida");
    if (r.status === 429) throw new ErrorAi("Groq está limitando las solicitudes (la capa gratuita tiene tope por minuto y por día); intenta de nuevo en un momento");
    if (r.status === 413) throw new ErrorAi("El brief es demasiado largo para el límite por minuto de Groq; acórtalo e intenta de nuevo");
    throw new ErrorAi(`La API de Groq respondió con error ${r.status}`);
  }
  throw new ErrorAi("El servidor no tiene configurada la llave de la API de Groq");
}

/** Pide al modelo el plan de content objects para un brief. Lanza ErrorAi con un mensaje para mostrar en pantalla. */
export async function interpretarBrief(brief: string, cat: Catalogo, pais: string): Promise<PlanBrief> {
  const Plan = z.object({
    generos: z.array(enumDe(cat.generos.map(x => x.valor))),
    categorias: z.array(enumDe(cat.categorias.map(x => x.valor))),
    ratings: z.array(enumDe(cat.ratings.map(x => x.valor))),
    idioma: enumDe([SIN_IDIOMA, ...cat.idiomas.map(x => x.valor)]),
    palabras_clave: z.array(z.string()),
    razon: z.string(),
  });
  const catalogo = [
    lista("Géneros", cat.generos), lista("Categorías IAB", cat.categorias),
    lista("Clasificaciones", cat.ratings), lista("Idiomas", cat.idiomas),
  ].join("\n\n");

  const usuario = `<mercado>${pais}</mercado>\n\n<catalogo>\n${catalogo}\n</catalogo>\n\n<brief>\n${brief}\n</brief>`;
  const p = PROVEEDOR === "groq"
    ? Plan.safeParse(await pedirAGroq(usuario, z.toJSONSchema(Plan))).data
    : await pedirAClaude(usuario, Plan);
  if (!p) throw new ErrorAi("El modelo no devolvió un plan que se pudiera leer. Intenta de nuevo");

  const unicos = <T>(xs: T[], n: number) => [...new Set(xs)].slice(0, n);
  return {
    paises: [pais],
    generos: unicos(p.generos, MAX.generos),
    categorias: unicos(p.categorias, MAX.categorias),
    ratings: unicos(p.ratings, MAX.ratings),
    idioma: p.idioma === SIN_IDIOMA ? "" : p.idioma,
    palabras_clave: unicos(p.palabras_clave.map(slug).filter(Boolean), MAX.palabras_clave),
    razon: p.razon.trim().slice(0, 900),
  };
}

async function pedirAClaude<T extends z.ZodType>(usuario: string, Plan: T): Promise<z.infer<T> | null> {
  const client = new Anthropic();
  let respuesta;
  try {
    respuesta = await client.messages.parse({
      model: MODELO,
      max_tokens: 16000,
      thinking: { type: "adaptive" },
      output_config: { effort: "medium", format: zodOutputFormat(Plan) },
      system: SISTEMA,
      messages: [{ role: "user", content: usuario }],
    });
  } catch (e) {
    if (e instanceof Anthropic.AuthenticationError) throw new ErrorAi("La llave de la API de Anthropic no es válida");
    if (e instanceof Anthropic.RateLimitError) throw new ErrorAi("La API de Anthropic está limitando las solicitudes; intenta de nuevo en un momento");
    if (e instanceof Anthropic.APIConnectionError) throw new ErrorAi("No se pudo conectar con la API de Anthropic");
    if (e instanceof Anthropic.APIError) throw new ErrorAi(`La API de Anthropic respondió con error ${e.status ?? ""}`.trim());
    throw e;
  }
  if (respuesta.stop_reason === "refusal") throw new ErrorAi("El modelo no quiso procesar ese brief. Revisa el texto e intenta de nuevo");
  return (respuesta.parsed_output ?? null) as z.infer<T> | null;
}
