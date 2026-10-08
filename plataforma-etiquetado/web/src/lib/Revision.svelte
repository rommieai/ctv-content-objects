<script lang="ts">
  import { untrack } from "svelte";
  import { api, fmt, nombreEstrato, type Ambito, type Opciones, type Registro } from "./api";
  import Tarjeta from "./Tarjeta.svelte";

  let { ambito, opciones, admin }: { ambito: Ambito; opciones: Opciones; admin: boolean } = $props();
  // el componente se recrea al cambiar de pestaña ({#key}), así que el ámbito es fijo aquí
  const fijo = untrack(() => ambito);
  const completo = fijo === "completo";

  // filtros (se recuerdan por ámbito en este navegador)
  const CLAVE = `etiquetas-ctv:filtros:${fijo}`;
  const inicial = (() => { try { return JSON.parse(localStorage.getItem(CLAVE) ?? "{}"); } catch { return {}; } })();
  let f = $state({ estado: "todos", campo: "", estrato: "", pais: "", q: "", llenados: "1", muestra: "0", pagina: 0, ...inicial });
  let qEscrito = $state(f.q);

  let registros = $state<Registro[]>([]);
  let total = $state(0);
  let porPagina = $state(20);
  let cargando = $state(false);
  let error = $state("");
  let progreso = $state<any>(null);
  let toastTxt = $state("");
  let toastVer = $state(false);

  const paginas = $derived(Math.max(1, Math.ceil(total / porPagina)));

  function toast(t: string) {
    toastTxt = t; toastVer = true;
    clearTimeout((toast as any).t);
    (toast as any).t = setTimeout(() => (toastVer = false), 1800);
  }

  let pedido = 0;
  async function cargar() {
    const n = ++pedido;
    cargando = true; error = "";
    const p = new URLSearchParams({ ambito: fijo, ...Object.fromEntries(Object.entries(f).map(([k, v]) => [k, String(v)])) });
    try {
      const d = await api(`/api/registros?${p}`);
      if (n !== pedido) return;
      registros = d.registros; total = d.total; porPagina = d.por_pagina;
      if (irA !== null) {
        const r = registros[irA % porPagina];
        irA = null;
        if (r) setTimeout(() => document.getElementById(`f${r.fila_id}`)?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
      }
    } catch (e) {
      if (n === pedido) error = (e as Error).message;
    }
    if (n === pedido) cargando = false;
  }
  async function cargarProgreso() {
    progreso = await api("/api/progreso").catch(() => progreso);
  }

  $effect(() => {
    const snapshot = JSON.stringify(f);
    try { localStorage.setItem(CLAVE, snapshot); } catch { /* sin almacenamiento: no pasa nada */ }
    untrack(cargar);
  });
  cargarProgreso();

  // búsqueda con espera, para no consultar en cada tecla
  let tq: ReturnType<typeof setTimeout>;
  function buscar(v: string) {
    qEscrito = v;
    clearTimeout(tq);
    tq = setTimeout(() => { f.q = v; f.pagina = 0; }, 350);
  }
  function cambiar() { f.pagina = 0; }
  function irPagina(p: number) { f.pagina = p; window.scrollTo(0, 0); }

  let tProg: ReturnType<typeof setTimeout>;
  async function veredicto(r: Registro, campo: string, valor: string, v: string) {
    const k = `${campo}|${valor}`;
    const antes = r.etiquetas[k];
    if (v) r.etiquetas[k] = { veredicto: v, correcto: antes?.correcto ?? "", ts: "" };
    else delete r.etiquetas[k];
    try {
      await api("/api/etiquetas", { metodo: "PUT", cuerpo: { fila_id: r.fila_id, campo, valor, veredicto: v, valor_correcto: antes?.correcto ?? "" } });
      clearTimeout(tProg);
      tProg = setTimeout(cargarProgreso, 400);
    } catch (e) {
      if (antes) r.etiquetas[k] = antes; else delete r.etiquetas[k];
      toast(`No se guardó: ${(e as Error).message}`);
    }
  }

  const esperas = new Map<string, ReturnType<typeof setTimeout>>();
  function conEspera(clave: string, fn: () => Promise<unknown>) {
    clearTimeout(esperas.get(clave));
    esperas.set(clave, setTimeout(() => fn().catch(e => toast(`No se guardó: ${(e as Error).message}`)), 500));
  }
  function correccion(r: Registro, campo: string, valor: string, texto: string) {
    const k = `${campo}|${valor}`;
    if (!r.etiquetas[k]) return;
    r.etiquetas[k].correcto = texto;
    conEspera(`c:${r.fila_id}|${k}`, () => api("/api/etiquetas", {
      metodo: "PUT", cuerpo: { fila_id: r.fila_id, campo, valor, veredicto: r.etiquetas[k]?.veredicto ?? "", valor_correcto: texto },
    }));
  }
  function nota(r: Registro, texto: string) {
    r.nota = texto;
    conEspera(`n:${r.fila_id}`, () => api("/api/notas", { metodo: "PUT", cuerpo: { fila_id: r.fila_id, nota: texto } }));
  }

  let irA: number | null = null;
  async function siguiente() {
    const { posicion } = await api("/api/siguiente");
    if (posicion < 0) { toast("No quedan pendientes"); return; }
    irA = posicion; // la muestra se ordena por número: la posición da la página y el lugar en ella
    qEscrito = "";
    const antes = JSON.stringify(f);
    Object.assign(f, { estado: "todos", campo: "", estrato: "", pais: "", q: "", pagina: Math.floor(posicion / porPagina) });
    if (JSON.stringify(f) === antes) cargar(); // mismos filtros: el $effect no se dispara
  }

  const prog = $derived(progreso?.muestra);
</script>

<header>
  <div class="wrap">
    {#if completo}
      <h1>Consolidado completo <small>{opciones.fuente}</small></h1>
      <div class="barra">
        <small>{fmt(opciones.total_filas)} filas · {fmt(opciones.filas_llenadas)} con algún valor llenado
          {#if progreso?.completo} · llevas {fmt(progreso.completo.etiquetas)} valores etiquetados en {fmt(progreso.completo.filas)} filas{/if}</small>
      </div>
    {:else}
      <h1>Revisión de la muestra <small>{opciones.version}</small></h1>
      <div class="barra">
        <div class="progreso">
          <div class="pista"><div class="lleno" style="width: {prog ? (100 * prog.hechos) / prog.total : 0}%"></div></div>
          <small>{#if prog}{fmt(prog.hechos)} de {fmt(prog.total)} valores revisados · {prog.tarjetas_revisadas} de {prog.tarjetas} tarjetas completas{/if}</small>
        </div>
        <button onclick={siguiente}>Ir al siguiente pendiente</button>
      </div>
    {/if}
  </div>
</header>

<main class="wrap">
  {#if !completo}
    <details class="ayuda" open={!prog?.hechos}>
      <summary>Cómo revisar</summary>
      <ul>
        <li>Cada tarjeta es una fila real del inventario: un título emitido por una app en un país. Los campos en <span class="muestra-chip llenado">naranja</span> son los que <b>llenamos de más</b> (el vendedor no los mandó). Los campos en <span class="muestra-chip corregido">rosa</span> son los que <b>corregimos</b>: el vendedor mandó un valor, lo consideramos equivocado y lo reemplazamos (abajo del campo dice qué mandó). Solo esos dos se revisan.</li>
        <li>Pregunta para cada campo naranja o rosa: <b>¿este valor es correcto para lo que esta app emite con este título?</b> Usa <i>Buscar</i> (Google con el título y la app) y, si aparece, la ficha IMDb de referencia.</li>
        <li><b>Correcto</b>: el valor describe bien el contenido. <b>Incorrecto</b>: no lo describe (si sabes el valor bueno, escríbelo). <b>No se sabe</b>: no encontraste cómo comprobarlo; no cuenta como correcto.</li>
        <li>Cuando un campo trae varios valores (varios códigos de categoría o varios géneros) se juzga <b>cada uno por separado</b>. Los marcados <b>MÁS ESPECÍFICO</b> son códigos de género que se agregaron a una categoría genérica.</li>
        <li>Los valores que <b>ya venían del vendedor</b> no se revisan, pero si ves uno equivocado márcalo con <b>Está mal</b>. Y si llenamos o cambiamos un campo cuando lo correcto era lo que venía (o dejarlo vacío), usa <b>Lo correcto era lo que venía antes</b>. Ambas son opcionales y no cuentan para el avance.</li>
        <li>La pregunta <b>¿la ficha IMDb es la misma obra que emite la app?</b> es opcional, pero ayuda mucho a medir los homónimos.</li>
        <li>Todo se guarda solo, en tu usuario, al momento de marcar. Puedes cerrar y seguir después desde cualquier equipo.</li>
      </ul>
    </details>
  {/if}

  <div class="leyenda">
    <span><span class="muestra-chip llenado">Valor llenado</span> se revisa</span>
    <span><span class="muestra-chip corregido">Valor corregido</span> el vendedor mandó otro; se revisa</span>
    <span><span class="muestra-chip vendedor">Valor del vendedor</span> contexto, no se revisa</span>
    <span><span class="muestra-chip vacio">vacío</span> no vino ni se llenó</span>
  </div>

  <div class="filtros">
    <select bind:value={f.estado} onchange={cambiar}>
      <option value="todos">Todas las tarjetas</option>
      <option value="pendientes">Con campos pendientes</option>
      <option value="revisadas">Revisadas por mí</option>
    </select>
    <select bind:value={f.campo} onchange={cambiar}>
      <option value="">Cualquier campo llenado</option>
      {#each opciones.campos as c}<option value={c.campo}>{c.nombre}</option>{/each}
      <option value="_extra">Con información extra de IMDb</option>
    </select>
    {#if admin}
      <select bind:value={f.estrato} onchange={cambiar} title="Método de relleno (no se muestra en la tarjeta)">
        <option value="">Cualquier método</option>
        {#each opciones.estratos as e}<option value={e}>{nombreEstrato(e)}</option>{/each}
      </select>
    {/if}
    <select bind:value={f.pais} onchange={cambiar}>
      <option value="">Todos los países</option>
      {#each opciones.paises as p}<option value={p}>{p}</option>{/each}
    </select>
    {#if completo}
      <select bind:value={f.llenados} onchange={cambiar}>
        <option value="1">Solo filas con valores llenados</option>
        <option value="0">Todas las filas</option>
      </select>
      <label class="check"><input type="checkbox" checked={f.muestra === "1"} onchange={ev => { f.muestra = ev.currentTarget.checked ? "1" : "0"; cambiar(); }} /> Solo las de la muestra</label>
    {/if}
    <input type="text" placeholder="Buscar título o app…" value={qEscrito} oninput={ev => buscar(ev.currentTarget.value)} />
  </div>

  {#if error}<div class="aviso">{error}</div>{/if}

  <div class="lista" class:cargando>
    {#each registros as r (r.fila_id)}
      <Tarjeta {r} mostrarFila={completo} onveredicto={veredicto} oncorreccion={correccion} onnota={nota} />
    {:else}
      {#if !cargando}<p class="nada">No hay tarjetas con este filtro.</p>{/if}
    {/each}
  </div>

  <div class="paginas">
    <button disabled={f.pagina === 0} onclick={() => irPagina(f.pagina - 1)}>‹ Anterior</button>
    <span>Página {fmt(f.pagina + 1)} de {fmt(paginas)} · {fmt(total)} tarjetas</span>
    <button disabled={f.pagina >= paginas - 1} onclick={() => irPagina(f.pagina + 1)}>Siguiente ›</button>
  </div>
</main>
<div class="toast" class:ver={toastVer}>{toastTxt}</div>

<style>
  header { position: sticky; top: 0; z-index: 5; background: var(--card); border-bottom: 1px solid var(--line); padding: 10px 16px; }
  h1 { font-size: 18px; margin: 0 0 6px; }
  h1 small { font-weight: 400; color: var(--ink2); font-size: 13px; }
  .barra { display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; color: var(--ink2); }
  .progreso { flex: 1 1 220px; min-width: 0; }
  .pista { height: 8px; background: var(--line); border-radius: 4px; overflow: hidden; }
  .lleno { height: 100%; background: var(--ok); transition: width .2s; }
  main { padding: 16px; }
  .ayuda { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; }
  .ayuda summary { cursor: pointer; font-weight: 600; }
  .ayuda li { margin: 4px 0; }
  .leyenda { display: flex; flex-wrap: wrap; gap: 10px 18px; margin: 0 0 14px; color: var(--ink2); font-size: 13px; align-items: center; }
  .filtros { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; align-items: center; }
  .check { font-size: 13px; color: var(--ink2); display: flex; gap: 4px; align-items: center; }
  .lista.cargando { opacity: .5; }
  .nada { color: var(--ink2); }
  .aviso { background: var(--bad-bg); color: var(--bad); padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; }
  .paginas { display: flex; gap: 6px; align-items: center; justify-content: center; margin: 18px 0 30px; flex-wrap: wrap; }
</style>
