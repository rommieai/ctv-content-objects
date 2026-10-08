// Bot que arma un Auction Package Deal en PubMatic Media Console (no hay acceso por API todavía).
// Port de scripts/crear_deal_pubmatic.py: mismo recorrido del asistente, mismos selectores.
//
//   Configuration  nombre, DSP y buyer (sin transaction fee, First Price, piso por defecto)
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

export interface PedidoDeal { nombre: string; paises: string[]; titulosCsv: string }
export interface DealCreado { id: number | null; pmId: string; enlace: string; estado: string }

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

    paso("Configuración: nombre, DSP y buyer");
    await page.goto(`${BASE}/deal/create/general`, { waitUntil: "domcontentloaded" });
    await pm(page, "input-deal-name").locator("input").waitFor({ state: "visible", timeout: 60_000 });
    await page.waitForTimeout(4000);
    await pm(page, "input-deal-name").locator("input").fill(p.nombre);
    await elegir(page, "dsp-select", PUBMATIC.dsp);
    await elegir(page, "buyer-select", PUBMATIC.buyer);
    const sinFee = pm(page, "radio-transaction-fee-no").locator("label");
    if (!((await sinFee.getAttribute("class")) ?? "").includes("hls-radio-box-selected")) await sinFee.click();

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
    if (!resumen.includes(p.nombre) || p.paises.some(x => !resumen.includes(x)) || !resumen.includes("1 Rule")) {
      throw new Error("El resumen de PubMatic no coincide con lo pedido; no se creó nada");
    }

    if (PUBMATIC.ensayo) return { id: null, pmId: "", enlace: "", estado: "ensayo" };

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
      enlace: c?.id ? `${BASE}/deal/edit/${c.id}/summary` : `${BASE}/deals`,
    };
  } finally {
    await nav.close().catch(() => {});
    rmSync(dir, { recursive: true, force: true });
  }
}
