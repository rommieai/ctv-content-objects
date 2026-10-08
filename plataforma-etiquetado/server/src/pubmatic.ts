// Bot que arma un Auction Package Deal en PubMatic Media Console (no hay acceso por API todavía).
// Port de scripts/crear_deal_pubmatic.py: mismo recorrido del asistente, mismos selectores.
//
//   Configuration  nombre, DSP, buyer y las condiciones: transaction fee, tipo de subasta, Media CPM y fechas
//   Inventory      publishers en Maximum Reach, Media Type Video, plataforma CTV
//   Targeting      países en Geography y una regla Content Object > Title con el CSV de títulos
//   Summary        se comprueba que diga lo pedido y se da el clic en "Create Auction Package"
//
// Un deal recién creado nace Live: en cuanto aparece en la lista se pausa. Nunca se deja activo.
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { Locator, Page } from "playwright";

const BASE = "https://apps.pubmatic.com/v3/common/pmc";
const LOGIN = "https://apps.pubmatic.com/login/demand?ref=https:%2F%2Fapps.pubmatic.com%2Fv3%2Fcommon%2Fpmc%2Fdeals";
const ESTADOS = ["Live", "Active", "Paused", "Pending", "Draft", "Inactive", "Expired", "Completed"];

export const PUBMATIC = {
  usuario: process.env.PUBMATIC_USUARIO ?? "",
  clave: process.env.PUBMATIC_CLAVE ?? "",
  dsp: process.env.PUBMATIC_DSP ?? "DV360",
  buyer: process.env.PUBMATIC_BUYER ?? "Ariadna Co DBM",
  // DEALS_ENSAYO=1: recorre todo el asistente y se detiene en el resumen, sin crear nada (para probar el bot)
  ensayo: process.env.DEALS_ENSAYO === "1",
};
export const pubmaticConfigurado = () => !!PUBMATIC.usuario && !!PUBMATIC.clave;

/** El deal se creó pero no se pudo pausar: sigue Live y alguien tiene que pausarlo a mano. */
export class DealSinPausar extends Error {
  constructor(public nombre: string, public pmId: string) {
    super(`El deal ${nombre}${pmId ? ` (${pmId})` : ""} se creó pero NO se pudo pausar: está Live. Hay que pausarlo a mano en PubMatic > Deals.`);
  }
}

/** Condiciones comerciales del deal, tal como se llenan en el paso Configuration. Montos en USD. */
export interface Condiciones {
  inicio: string;                        // AAAA-MM-DD; "" = la fecha que propone PubMatic (hoy)
  fin: string;                           // AAAA-MM-DD; "" = Ongoing (sin fecha de fin)
  fee: "no" | "fijo" | "porcentaje";     // Transaction Fee: No, o Yes con CPM Fixed / Percentage
  feeValor: number;                      // dólares de CPM (fijo) o % (porcentaje)
  subasta: "first" | "fixed";            // Auction Type
  mediaCpm: number | null;               // Fixed Price: Media CPM (obligatorio). First Price: Custom Media Floor (opcional)
}
export interface PedidoDeal { nombre: string; paises: string[]; titulosCsv: string; condiciones: Condiciones }
export interface DealCreado { id: number | null; pmId: string; enlace: string; estado: string; resumen: string }

const pm = (page: Page, id: string) => page.locator(`[data-pm-id="${id}"]`);
const texto = async (page: Page) => (await page.innerText("body")).split("\n").map(l => l.trim()).filter(Boolean).join(" | ");

async function entrar(page: Page) {
  // sin sesión PubMatic manda al login de publisher; la cuenta es de Media Console (demand)
  await page.goto(LOGIN, { waitUntil: "domcontentloaded" });
  await page.locator("#okta-signin-password").waitFor({ state: "visible", timeout: 30_000 });
  await page.locator("#okta-signin-username").fill(PUBMATIC.usuario);
  await page.locator("#okta-signin-password").fill(PUBMATIC.clave);
  await page.locator("#okta-signin-submit").click();
  for (let i = 0; i < 120 && page.url().includes("/login"); i++) await page.waitForTimeout(500);
  if (page.url().includes("/login")) {
    const aviso = page.locator(".okta-form-infobox-error, .o-form-error-container").first();
    throw new Error("El login de PubMatic no pasó: " + ((await aviso.count()) ? (await aviso.innerText()).trim() : "¿clave vencida o verificación adicional?"));
  }
}

async function elegir(page: Page, selectPm: string, opcion: string) {
  await pm(page, selectPm).locator("hls-select-trigger").click();
  await page.waitForTimeout(1500);
  await page.locator('input[placeholder="Search"]:visible').last().fill(opcion);
  await page.waitForTimeout(2500);
  const op = page.locator("hls-select-list").getByText(opcion, { exact: true });
  if (!(await op.count())) throw new Error(`PubMatic no ofrece la opción "${opcion}" en ${selectPm}`);
  await op.first().click();
  await page.waitForTimeout(800);
  await page.keyboard.press("Escape");
  await page.waitForTimeout(1000);
}

const mmddaaaa = (iso: string) => `${iso.slice(5, 7)}/${iso.slice(8, 10)}/${iso.slice(0, 4)}`;

async function escribirNumero(campo: Locator, valor: number) {
  await campo.waitFor({ state: "visible", timeout: 15_000 });
  await campo.fill(String(Number(valor.toFixed(2))));
  await campo.press("Tab");
  await campo.page().waitForTimeout(600);
}

const MESES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

/** Elige una fecha en el calendario de PubMatic (los campos mm/dd/aaaa no aceptan texto: solo el calendario los cambia). */
async function escribirFecha(page: Page, selector: string, iso: string) {
  const caja = pm(page, selector);
  const leer = async () => (await Promise.all(["dp-input-mm", "dp-input-dd", "dp-input-yyyy"].map(x => caja.locator(`[data-pm-id="${x}"]`).inputValue()))).join("/");
  if ((await leer()) === mmddaaaa(iso)) return;
  const buscado = `${MESES[Number(iso.slice(5, 7)) - 1]} ${iso.slice(0, 4)}`, dia = String(Number(iso.slice(8, 10)));
  await caja.locator('[data-pm-id="dp-input-mm"]').click();
  const cal = page.locator('[data-pm-id="date-picker-calendar"]');
  await cal.waitFor({ state: "visible", timeout: 15_000 });
  const limpio = (t: string) => t.replace(/\s+/g, " ").trim();
  const izq = cal.locator('[data-pm-id="calendar-prev-month"]'), der = cal.locator('[data-pm-id="calendar-next-month"]');
  let mes: Locator | null = null;
  // el calendario muestra dos meses; se avanza hasta que uno de los dos sea el buscado
  for (let i = 0; i < 40 && !mes; i++) {
    const tituloIzq = limpio(`${await izq.locator(".hls-calendar-select-month hls-select-trigger").first().innerText()} ${await izq.locator(".hls-calendar-select-year hls-select-trigger").first().innerText()}`);
    const tituloDer = limpio(await der.locator(".hls-calendar-month-2-caption span").first().innerText());
    if (tituloIzq === buscado) mes = izq;
    else if (tituloDer === buscado) mes = der;
    else {
      await der.locator('[data-pm-id="next-month"]').click();
      await page.waitForTimeout(500);
    }
  }
  if (mes) {
    const celda = mes.locator(".hls-calendar-dates span:not(.blank):not(.not-in-calendar)").filter({ hasText: new RegExp("^\\s*" + dia + "\\s*$") });
    if (await celda.count()) await celda.first().click();
    await page.waitForTimeout(800);
  }
  // si el calendario sigue abierto (o la fecha no se podía elegir) su fondo tapa el formulario: se cierra
  if (await cal.isVisible().catch(() => false)) { await page.keyboard.press("Escape"); await page.waitForTimeout(600); }
  const quedo = await leer();
  if (quedo !== mmddaaaa(iso)) throw new Error(`PubMatic no aceptó la fecha ${mmddaaaa(iso)} (dejó ${quedo}). No se creó nada`);
}

/** Transaction Fee, Auction Type, Media CPM y Transaction Date del paso Configuration. */
async function condiciones(page: Page, c: Condiciones) {
  const elegirRadio = async (id: string) => {
    const etiqueta = pm(page, id).locator("label");
    if (((await etiqueta.getAttribute("class")) ?? "").includes("hls-radio-box-selected")) return;
    await etiqueta.click();
    await page.waitForTimeout(1200);
  };
  const dolares = (id: string) => pm(page, id).locator('[data-pm-id="currency-picker-value"]');

  await elegirRadio(c.fee === "no" ? "radio-transaction-fee-no" : "radio-transaction-fee-yes");
  if (c.fee !== "no") {
    await pm(page, "switcher-cpm").getByText(c.fee === "fijo" ? "Fixed" : "Percentage", { exact: true }).click();
    await page.waitForTimeout(1200);
    await escribirNumero(c.fee === "fijo" ? dolares("transaction-fee-fixed-input") : pm(page, "input-deal-transaction-fee-percent").locator("input"), c.feeValor);
  }

  await elegirRadio(c.subasta === "fixed" ? "fixed-price-auction-type" : "first-price-auction-type");
  if (c.subasta === "fixed") {
    if (c.mediaCpm === null) throw new Error("Fixed Price necesita un Media CPM");
    await escribirNumero(dolares("fixed-price-cpm"), c.mediaCpm);
  } else if (c.mediaCpm !== null) {
    await pm(page, "custom-floor-toggle").click();
    await page.waitForTimeout(1200);
    await escribirNumero(dolares("custom-floor-cpm"), c.mediaCpm);
  }

  if (c.inicio) await escribirFecha(page, "transaction-date-pickerstart", c.inicio);
  if (c.fin) {
    await pm(page, "deal-ongoing-checkbox").locator("label").click();   // viene marcado: al quitarlo aparece la fecha de fin
    await page.waitForTimeout(1200);
    await escribirFecha(page, "transaction-date-pickerend", c.fin);
  }

  // PubMatic valida límites que aquí no se conocen (fee máximo, fechas pasadas...): si marca algo, no se sigue
  await page.waitForTimeout(800);
  const invalidos = page.locator("hls-form-control.hls-form-control-invalid");
  if (await invalidos.count()) {
    const motivos = (await invalidos.allInnerTexts()).map(t => t.split("\n").map(x => x.trim()).filter(Boolean).pop() ?? "").filter(Boolean);
    throw new Error("PubMatic rechazó las condiciones: " + ([...new Set(motivos)].join("; ") || "hay un campo inválido") + ". No se creó nada");
  }
  if (await page.getByRole("button", { name: "Next" }).isDisabled()) throw new Error("PubMatic no deja avanzar con esas condiciones. No se creó nada");
}

/** Lo que el resumen de PubMatic debe decir para que el deal sea el pedido. */
function comprobarResumen(resumen: string, p: PedidoDeal) {
  const c = p.condiciones, faltan: string[] = [];
  const debe = (trozo: string, que: string) => { if (!resumen.includes(trozo)) faltan.push(que); };
  debe(p.nombre, "el nombre");
  for (const pais of p.paises) debe(pais, pais);
  debe("1 Rule", "la regla de títulos");
  debe(`Auction Type | ${c.subasta === "fixed" ? "Fixed Price" : "First Price"}`, "el tipo de subasta");
  debe(`Transaction Fee | ${c.fee === "no" ? "No" : "Yes"}`, "el transaction fee");
  const n = (x: number) => String(Number(x.toFixed(2)));
  if (c.fee === "fijo") debe(`Transaction Fee CPM | $ ${n(c.feeValor)}`, "el monto del transaction fee");
  if (c.fee === "porcentaje") debe(`Transaction Fee CPM | ${n(c.feeValor)}%`, "el porcentaje del transaction fee");
  if (c.subasta === "fixed") debe(`Media CPM | $ ${n(c.mediaCpm ?? 0)}`, "el Media CPM");
  else if (c.mediaCpm !== null) debe(`Custom Media Floor | $ ${n(c.mediaCpm)}`, "el piso de media");
  if (c.inicio) debe(`Start Date- ${mmddaaaa(c.inicio)}`, "la fecha de inicio");
  debe(c.fin ? `End Date- ${mmddaaaa(c.fin)}` : "On Going", "la fecha de fin");
  if (faltan.length) throw new Error(`El resumen de PubMatic no coincide con lo pedido (${faltan.join(", ")}); no se creó nada`);
}

async function siguiente(page: Page, trozo: string) {
  await page.getByRole("button", { name: "Next" }).click();
  // la consola cambia de paso sin recargar: se espera a que cambie la dirección
  for (let i = 0; i < 120 && !page.url().includes(trozo); i++) await page.waitForTimeout(500);
  if (!page.url().includes(trozo)) throw new Error(`El asistente de PubMatic no avanzó a ${trozo}`);
  await page.waitForTimeout(5000);
}

async function filaDeal(page: Page, nombre: string): Promise<{ fila: Locator; estado: string; pmId: string }> {
  await page.goto(`${BASE}/deals`, { waitUntil: "domcontentloaded" });
  await page.getByText(nombre, { exact: true }).first().waitFor({ state: "visible", timeout: 60_000 });
  await page.waitForTimeout(3000);
  const fila = page.locator("tbody tr").filter({ has: page.getByText(nombre, { exact: true }) }).first();
  const celdas = (await fila.innerText()).split("\n").map(c => c.trim()).filter(Boolean);
  return { fila, estado: celdas.find(c => ESTADOS.includes(c)) ?? "?", pmId: celdas.find(c => /^PM-[A-Z0-9-]+$/.test(c)) ?? "" };
}

async function pausar(page: Page, nombre: string) {
  let d = await filaDeal(page, nombre);
  if (d.estado === "Paused") return d;
  await d.fila.locator('[data-pm-id="hls-tra-ckbx"] label').click();
  await page.waitForTimeout(1500);
  const boton = pm(page, "hls-tba-action-button-Pause");
  if (!(await boton.count())) throw new Error(`No aparece el botón Pause del deal ${nombre}`);
  await boton.click();
  await page.waitForTimeout(1500);
  const confirmar = pm(page, "pause-deal-modal").getByRole("button").filter({ hasText: /pause|confirm|yes|ok/i });
  if (await confirmar.count()) await confirmar.last().click();
  await page.waitForTimeout(5000);
  d = await filaDeal(page, nombre);
  if (d.estado !== "Paused") throw new Error(`El deal ${nombre} quedó en estado ${d.estado} después de pausar`);
  return d;
}

/** Crea el deal y lo deja en pausa. `paso` recibe el avance para mostrarlo en la web. */
export async function crearDeal(p: PedidoDeal, paso: (msg: string) => void): Promise<DealCreado> {
  const { chromium } = await import("playwright");
  const dir = mkdtempSync(join(tmpdir(), "deal-"));
  const csv = join(dir, "Title_is.csv");
  writeFileSync(csv, p.titulosCsv);
  const nav = await chromium.launch({ headless: true });
  let creado: { id: number | null; pmId: string } | null = null;
  try {
    const page = await (await nav.newContext({ viewport: { width: 1600, height: 1100 } })).newPage();
    page.on("response", async r => {
      if (!r.url().includes("/api/curateddeals/create") || r.request().method() !== "POST") return;
      const j = await r.json().catch(() => null);
      if (j?.id) creado = { id: Number(j.id), pmId: String(j.dealId ?? "") };
    });

    paso("Iniciando sesión en PubMatic");
    await entrar(page);
    await page.goto(`${BASE}/deals`, { waitUntil: "domcontentloaded" });
    await page.locator("tbody tr").first().waitFor({ state: "attached", timeout: 60_000 }).catch(() => {});
    await page.waitForTimeout(4000);
    if (await page.getByText(p.nombre, { exact: true }).count()) throw new Error(`Ya existe un deal llamado ${p.nombre} en PubMatic`);

    paso("Configuración: nombre, DSP, buyer y condiciones");
    await page.goto(`${BASE}/deal/create/general`, { waitUntil: "domcontentloaded" });
    await pm(page, "input-deal-name").locator("input").waitFor({ state: "visible", timeout: 60_000 });
    await page.waitForTimeout(4000);
    await pm(page, "input-deal-name").locator("input").fill(p.nombre);
    await elegir(page, "dsp-select", PUBMATIC.dsp);
    await elegir(page, "buyer-select", PUBMATIC.buyer);
    await condiciones(page, p.condiciones);

    paso("Inventario: Video en CTV");
    await siguiente(page, "/deal/create/inventory");
    // Banner y Desktop vienen marcados y los tiles son de selección múltiple: se marca Video y CTV
    // (el tile de CTV se llama tile-native en la página) y se desmarcan los dos de fábrica.
    for (const tile of ["tile-video", "tile-native", "tile-banner", "tile-desktop"]) {
      await pm(page, tile).click();
      await page.waitForTimeout(1500);
    }

    paso("Targeting: países");
    await siguiente(page, "/deal/create/targeting");
    await page.getByText("Geography", { exact: true }).first().click();
    await page.waitForTimeout(3000);
    for (const pais of p.paises) {
      await page.locator('input[placeholder*="earch"]:visible').first().fill(pais);
      await page.waitForTimeout(3000);
      await page.getByText(pais, { exact: true }).first().click();
      await page.waitForTimeout(2000);
      if (!(await texto(page)).split("Selected").pop()!.includes(pais)) throw new Error(`${pais} no quedó seleccionado en Geography`);
    }

    paso("Targeting: lista de títulos");
    await page.getByText("Content Object", { exact: true }).first().click();
    await page.waitForTimeout(3000);
    await page.getByText("Add Rule").last().click();
    await page.waitForTimeout(1500);
    await page.getByText("Select...", { exact: true }).first().click();
    await page.waitForTimeout(1000);
    await page.locator('input[placeholder="Search"]:visible').last().fill("Title");
    await page.waitForTimeout(1500);
    await page.getByText("Title", { exact: true }).last().click();
    await page.waitForTimeout(1500);
    await page.getByText("Upload", { exact: true }).first().click();
    await page.waitForTimeout(1000);
    await page.locator('input[type="file"]').setInputFiles(csv);
    await page.waitForTimeout(4000);
    const guardar = page.getByRole("button", { name: "Save" }).last();
    if (await guardar.isDisabled()) throw new Error("PubMatic no aceptó el CSV de títulos");
    await guardar.click();
    await page.waitForTimeout(2500);

    paso("Revisando el resumen");
    await siguiente(page, "/deal/create/summary");
    const resumen = await texto(page);
    if (!resumen.includes("Media Type | Video | Platform | CTV | Ad Sizes")) throw new Error("El resumen de PubMatic no dice solo Video + CTV; no se creó nada");
    // la parte de Configuration del resumen, tal como la muestra PubMatic: queda guardada con el trabajo
    const condicionesPm = resumen.split("Configuration | ").pop()!.split(" | Inventory | ")[0].replaceAll(" | ", " · ");
    console.log(`deal ${p.nombre}: resumen de PubMatic -> ${condicionesPm}`);
    comprobarResumen(resumen, p);

    if (PUBMATIC.ensayo) return { id: null, pmId: "", enlace: "", estado: "ensayo", resumen: condicionesPm };

    paso("Creando el deal");
    await page.getByRole("button", { name: "Create Auction Package" }).click();
    for (let i = 0; i < 240 && !/\/pmc\/deals\/?(\?.*)?$/.test(page.url()); i++) await page.waitForTimeout(500);
    await page.waitForTimeout(5000);

    paso("Pausando el deal");
    const c = creado as { id: number | null; pmId: string } | null;
    let d: Awaited<ReturnType<typeof pausar>> | null = null;
    for (let intento = 0; intento < 2 && !d; intento++) d = await pausar(page, p.nombre).catch(() => null);
    if (!d) throw new DealSinPausar(p.nombre, c?.pmId ?? "");
    return {
      id: c?.id ?? null, pmId: c?.pmId || d.pmId, estado: d.estado,
      enlace: c?.id ? `${BASE}/deal/edit/${c.id}/summary` : `${BASE}/deals`, resumen: condicionesPm,
    };
  } finally {
    await nav.close().catch(() => {});
    rmSync(dir, { recursive: true, force: true });
  }
}
