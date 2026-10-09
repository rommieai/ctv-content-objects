<script lang="ts">
  import { api, fmt } from "./api";

  // AI Deals: el brief de la campaña decide los content objects del deal; el CPM se reparte mitad fee y mitad puja.
  interface Medida { requests: number; pct_universo: number; pct_vendido: number | null; ecpm: number | null }
  interface Plan {
    paises: string[]; generos: string[]; categorias: string[]; ratings: string[]; idioma: string; palabras_clave: string[]; razon: string;
  }
  interface OpcionesAi {
    dsps: string[]; dsp_defecto: string; campanas: string[]; formatos: string[]; cpm: { min: number; max: number };
    meta: Record<string, string> | null;
    configurado: { datos: boolean; ai: boolean; pubmatic: boolean; ensayo: boolean };
  }
  interface VistaPlan {
    plan: Plan; nombre: string; cpm: number; fee: number; media_cpm: number;
    nativo: Medida; recomendado: Medida; lista: Medida;
    titulos: { total: number; en_csv: number; top: { titulo: string; requests: number }[] };
    categorias: { valor: string; nombre: string }[];
  }
  interface Trabajo {
    id: number; tipo: string; nombre: string; estado: "en_cola" | "corriendo" | "listo" | "error" | "sin_pausar"; detalle: string;
    pm_id: string; enlace: string; titulos: number; creado: string; de: string; dsp: string; cuenta: string; cpm: string;
    brief: string; plan: Plan | null; resumen_pm: string;
  }

  let opciones = $state<OpcionesAi | null>(null);
  let error = $state("");
  let brief = $state("");
  let dsp = $state("");
  let cuenta = $state("");
  let cpm = $state<number | null>(null);
  let campana = $state("");
  let formato = $state("");
  let vista = $state<VistaPlan | null>(null);
  let pedido = $state("");            // los campos con los que se calculó `vista`
  let pensando = $state(false);
  let confirmo = $state(false);
  let creando = $state(false);
  let errorCrear = $state("");
  let trabajos = $state<Trabajo[]>([]);
  let ultimo = $state<number | null>(null);   // el trabajo que se acaba de lanzar desde aquí
  let detalle = $state<HTMLDialogElement | null>(null);   // ventana con los content objects y el inventario del deal

  const usd = (x: number | null | undefined) => (x === null || x === undefined ? "—" : `$${x.toFixed(2)}`);
  const pc = (x: number | null | undefined) => (x === null || x === undefined ? "—" : `${(100 * x).toFixed(1)}%`);
  const fecha = (s: string) => new Date(s).toLocaleString("es-MX", { dateStyle: "medium", timeStyle: "short" });
  const mayus = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
  const ESTADO: Record<Trabajo["estado"], string> = {
    en_cola: "En cola", corriendo: "Creando…", listo: "Creado, en pausa", error: "Falló", sin_pausar: "Creado pero SIN PAUSAR",
  };

  const entrada = () => ({ brief: brief.trim(), dsp, cuenta: cuenta.trim(), cpm, campana, formato });
  const falta = $derived(
    brief.trim().length < 20 ? "Escribe el brief de la campaña."
    : !dsp ? "Elige el DSP."
    : !opciones?.dsps.includes(dsp) ? "Ese DSP no está en la lista de PubMatic: elígelo de las sugerencias."
    : !cuenta.trim() ? "Escribe el ID de la cuenta en el DSP."
    : typeof cpm !== "number" ? "Escribe el CPM."
    : opciones && (cpm < opciones.cpm.min || cpm > opciones.cpm.max) ? `El CPM debe estar entre $${opciones.cpm.min} y $${opciones.cpm.max}.`
    : "");
  const viejo = $derived(!!vista && pedido !== JSON.stringify(entrada()));
  const activos = $derived(trabajos.some(t => t.estado === "en_cola" || t.estado === "corriendo"));
  const hecho = $derived(trabajos.find(t => t.id === ultimo) ?? null);
  const mitad = $derived(typeof cpm === "number" && cpm > 0 ? Math.round(cpm * 50) / 100 : null);

  api<OpcionesAi>("/api/admin/deals/ai/opciones").then(o => {
    opciones = o;
    dsp = o.dsp_defecto; campana = o.campanas[0]; formato = o.formatos[0];
  }).catch(e => (error = e.message));
  const cargarTrabajos = () => api<{ trabajos: Trabajo[] }>("/api/admin/deals/trabajos")
    .then(r => (trabajos = r.trabajos.filter(t => t.tipo === "ai"))).catch(() => {});
  cargarTrabajos();
  $effect(() => {
    if (!activos) return;
    const t = setInterval(cargarTrabajos, 4000);
    return () => clearInterval(t);
  });

  async function armar() {
    pensando = true; error = ""; errorCrear = ""; confirmo = false; ultimo = null;
    const e = entrada();
    try {
      vista = await api<VistaPlan>("/api/admin/deals/ai/plan", { metodo: "POST", cuerpo: e });
      pedido = JSON.stringify(e);
    } catch (x) { error = (x as Error).message; vista = null; }
    pensando = false;
  }
  async function crear() {
    creando = true; errorCrear = "";
    try {
      const r = await api<{ id: number }>("/api/admin/deals/ai/crear", { metodo: "POST", cuerpo: { ...entrada(), plan: vista!.plan, confirmo: true } });
      ultimo = r.id; confirmo = false;
      await cargarTrabajos();
    } catch (x) { errorCrear = (x as Error).message; }
    creando = false;
  }
</script>

<main class="wrap">
  <h1>AI Deals</h1>
  {#if error}<div class="aviso">{error}</div>{/if}
  {#if opciones}
    {#if !opciones.configurado.datos}<div class="aviso">Todavía no se ha cargado la base de deals (deals.db).</div>{/if}
    {#if !opciones.configurado.ai}<div class="aviso">Este servidor no tiene la llave del modelo que lee el brief (ANTHROPIC_API_KEY o GROQ_API_KEY).</div>{/if}

    <section class="caja">
      <h2>1. La campaña</h2>
      <label class="campo"><span class="etq">Brief de la campaña</span>
        <textarea bind:value={brief} rows="6" maxlength="6000"
          placeholder="Marca, producto, público, mercados y tono. Con eso se eligen los content objects del deal."></textarea>
      </label>
      <div class="dos">
        <label class="campo"><span class="etq">DSP que recibe el deal</span>
          <input type="text" list="ai-dsps" bind:value={dsp} placeholder="Escribe para buscar" />
          <datalist id="ai-dsps">{#each opciones.dsps as x (x)}<option value={x}></option>{/each}</datalist>
        </label>
        <label class="campo"><span class="etq">ID de la cuenta en el DSP</span>
          <input type="text" bind:value={cuenta} maxlength="40" placeholder="Seat ID, ej. 1455254" />
        </label>
        <label class="campo"><span class="etq">CPM (USD)</span>
          <span class="monto"><span>$</span>
            <input type="number" bind:value={cpm} min={opciones.cpm.min} max={opciones.cpm.max} step="0.01" placeholder="4.00" /></span>
        </label>
        <label class="campo"><span class="etq">Tipo de campaña</span>
          <select bind:value={campana}>{#each opciones.campanas as x (x)}<option value={x}>{x}</option>{/each}</select>
        </label>
        <label class="campo"><span class="etq">Formato</span>
          <select bind:value={formato}>{#each opciones.formatos as x (x)}<option value={x}>{x}</option>{/each}</select>
        </label>
      </div>
      {#if mitad !== null}<small class="nota">El CPM se reparte mitad y mitad: {usd(mitad)} de transaction fee y {usd((cpm ?? 0) - mitad)} de puja (Media CPM a precio fijo).</small>{/if}
      <div class="botones">
        <button class="primario" disabled={!!falta || pensando || !opciones.configurado.ai || !opciones.configurado.datos} onclick={armar}>
          {pensando ? "Leyendo el brief…" : "Armar el deal"}</button>
        {#if falta}<small class="nota">{falta}</small>{/if}
      </div>
    </section>

    {#if vista}
      <section class="caja" class:viejo>
        <div class="cab">
          <h2>2. El deal</h2>
          <button type="button" class="info" aria-label="Ver los content objects y el inventario de este deal" title="Detalle del deal"
            onclick={() => detalle?.showModal()}>i</button>
        </div>
        {#if viejo}<div class="aviso suave">Cambiaste los datos de la campaña: vuelve a dar clic en «Armar el deal».</div>{/if}
        <dl class="ficha">
          <dt>Nombre del deal</dt><dd class="mono">{hecho?.nombre ?? vista.nombre}</dd>
          <dt>ID del deal</dt>
          <dd>{#if hecho?.pm_id}{#if hecho.enlace}<a href={hecho.enlace} target="_blank" rel="noopener">{hecho.pm_id}</a>{:else}{hecho.pm_id}{/if}
            {:else if hecho}<span class="estado {hecho.estado}">{ESTADO[hecho.estado]}</span> <small>{hecho.detalle}</small>
            {:else}<span class="nota">se asigna al crearlo en PubMatic</span>{/if}</dd>
          <dt>CPM</dt><dd>{usd(vista.cpm)} <small>({usd(vista.fee)} fee + {usd(vista.media_cpm)} puja)</small></dd>
        </dl>

        {#if !hecho || hecho.estado === "error"}
          <div class="crear">
            <label class="confirmo"><input type="checkbox" bind:checked={confirmo} /> Entiendo que esto crea un deal real en la cuenta de PubMatic</label>
            <div class="botones">
              <button class="primario" disabled={viejo || creando || !confirmo || !opciones.configurado.pubmatic || !vista.titulos.en_csv} onclick={crear}>
                {creando ? "Enviando…" : "Crear en PubMatic (en pausa)"}</button>
            </div>
            {#if !vista.titulos.en_csv}<small class="nota falta">Con esos content objects no hay títulos en el inventario: ajusta el brief.</small>{/if}
            {#if !opciones.configurado.pubmatic}<small class="nota">Este servidor no tiene las credenciales de PubMatic.</small>{/if}
            {#if opciones.configurado.ensayo}<small class="nota">Servidor en modo ensayo: el bot recorre el asistente de PubMatic pero no crea el deal.</small>{/if}
            {#if errorCrear}<div class="aviso">{errorCrear}</div>{/if}
          </div>
        {/if}
      </section>
    {/if}

    {#if vista}
      <!-- el detalle va aparte: se abre con el botón «i» del deal; un clic fuera de la ventana la cierra -->
      <dialog bind:this={detalle} class="detalle" onclick={e => { if (e.target === detalle) detalle?.close(); }}>
        <div class="cab">
          <h2>Detalle del deal</h2>
          <button type="button" onclick={() => detalle?.close()}>Cerrar</button>
        </div>

        <h3>Content objects que se aplican, según el brief</h3>
        <p class="razon">{vista.plan.razon}</p>
        <dl class="ficha">
          <dt>Países</dt><dd>{vista.plan.paises.join(", ")}</dd>
          {#if vista.plan.generos.length}<dt>Género</dt><dd>{vista.plan.generos.map(mayus).join(", ")}</dd>{/if}
          {#if vista.categorias.length}<dt>Categoría IAB</dt><dd>{vista.categorias.map(c => c.valor + (c.nombre ? ` · ${c.nombre}` : "")).join(", ")}</dd>{/if}
          {#if vista.plan.ratings.length}<dt>Clasificación</dt><dd>{vista.plan.ratings.join(", ")}</dd>{/if}
          {#if vista.plan.idioma}<dt>Idioma</dt><dd>{vista.plan.idioma}</dd>{/if}
        </dl>

        <h3>Inventario histórico con el que se armó</h3>
        <dl class="ficha">
          {#if opciones.meta?.ventana}<dt>Datos de</dt><dd>{opciones.meta.ventana}</dd>{/if}
          <dt>Requests</dt><dd>{fmt(vista.lista.requests)} <small>({pc(vista.lista.pct_universo)} de esos países)</small></dd>
          <dt>Títulos</dt><dd>{fmt(vista.titulos.en_csv)}</dd>
          <dt>Vendido</dt><dd>{pc(vista.lista.pct_vendido)}</dd>
          <dt>eCPM histórico</dt><dd>{usd(vista.lista.ecpm)}</dd>
        </dl>
        <p class="nota">En PubMatic esos content objects viajan como la lista de los {fmt(vista.titulos.en_csv)} títulos que nuestra base clasifica así{vista.plan.idioma ? `, más la regla Language is ${vista.plan.idioma}` : ""}.
          Con los filtros de PubMatic solos se alcanzarían {fmt(vista.nativo.requests)} requests.</p>
        {#if vista.titulos.top.length}
          <div class="scroll">
            <table>
              <thead><tr><th>Títulos con más requests</th><th>Requests</th></tr></thead>
              <tbody>
                {#each vista.titulos.top.slice(0, 10) as t (t.titulo)}<tr><td>{t.titulo}</td><td>{fmt(t.requests)}</td></tr>{/each}
              </tbody>
            </table>
          </div>
        {/if}
      </dialog>
    {/if}

    {#if trabajos.length}
      <section class="caja">
        <h2>Deals creados con AI Deals</h2>
        <div class="scroll">
          <table>
            <thead><tr><th>Deal</th><th>ID</th><th>CPM</th><th>DSP · cuenta</th><th>Content objects</th><th>Estado</th><th>Quién</th><th>Cuándo</th></tr></thead>
            <tbody>
              {#each trabajos as t (t.id)}
                <tr>
                  <td class="mono">{t.nombre}</td>
                  <td>{#if t.enlace}<a href={t.enlace} target="_blank" rel="noopener">{t.pm_id || "abrir"}</a>{:else}{t.pm_id || "—"}{/if}</td>
                  <td>{t.cpm ? usd(+t.cpm) : "—"}</td>
                  <td class="izq">{t.dsp} · {t.cuenta}</td>
                  <td class="izq" title={t.brief}>{t.plan ? [t.plan.generos.map(mayus).join(", "), t.plan.categorias.join(", "), t.plan.ratings.join(", "), t.plan.idioma, t.plan.paises.join(", ")].filter(Boolean).join(" · ") : "—"}</td>
                  <td class="izq"><span class="estado {t.estado}">{ESTADO[t.estado]}</span>{#if t.estado !== "listo"}<br /><small>{t.detalle}</small>{/if}</td>
                  <td class="izq">{t.de}</td><td>{fecha(t.creado)}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </section>
    {/if}
  {:else if !error}
    <p>Cargando…</p>
  {/if}
</main>

<style>
  main { padding: 16px; }
  h1 { font-size: 20px; margin: 4px 0 6px; }
  h2 { font-size: 17px; margin: 0 0 4px; }
  h3 { font-size: 14px; margin: 10px 0 0; }
  .nota { color: var(--ink2); font-size: 13px; margin: 0; }
  .falta { color: var(--bad); }
  .caja { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 16px; margin-top: 14px; display: grid; gap: 12px; }
  .caja.viejo > :not(.cab):not(.aviso) { opacity: .45; }
  .cab { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
  .cab h2 { margin: 0; }
  .info {
    flex: 0 0 auto; width: 28px; height: 28px; padding: 0; border-radius: 50%; border-color: var(--accent); color: var(--lila);
    font: italic 700 15px/1 Georgia, "Times New Roman", serif;
  }
  .detalle {
    width: min(640px, calc(100vw - 32px)); max-height: calc(100vh - 48px); overflow-y: auto; padding: 18px; color: var(--ink);
    background: var(--card); border: 1px solid var(--accent); border-radius: 14px;
    box-shadow: 0 0 20px 5px rgba(163, 87, 250, .25), 0 10px 30px rgba(0, 0, 0, .5);
  }
  .detalle[open] { display: grid; gap: 12px; }
  .detalle::backdrop { background: rgba(8, 0, 23, .72); }
  .campo { display: grid; gap: 4px; min-width: 0; }
  .etq { font-size: 13px; color: var(--ink2); }
  .dos { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; }
  .campo input[type=text], .campo select { width: 100%; }
  textarea, input[type=number] {
    font: inherit; padding: 8px; border: 1px solid var(--line); border-radius: 6px; background: var(--card); color: var(--ink);
    min-width: 0; max-width: 100%;
  }
  textarea { width: 100%; resize: vertical; }
  input[type=number] { width: 100%; font-variant-numeric: tabular-nums; }
  .monto { display: flex; align-items: center; gap: 6px; color: var(--ink2); }
  .botones { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; }
  .ficha { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 6px 16px; margin: 0; font-size: 14px; }
  .ficha dt { color: var(--ink2); }
  .ficha dd { margin: 0; font-weight: 600; overflow-wrap: anywhere; }
  .ficha dd small { font-weight: 400; color: var(--ink2); }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; }
  .razon { margin: 0; font-size: 14px; }
  .crear { display: grid; gap: 10px; }
  .confirmo { display: flex; gap: 8px; align-items: center; font-size: 14px; }
  .scroll { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; font-variant-numeric: tabular-nums; }
  th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
  th:first-child, td:first-child, td.izq { text-align: left; white-space: normal; }
  th { color: var(--ink2); font-weight: 600; }
  tr:last-child td { border-bottom: 0; }
  .aviso { background: var(--bad-bg); color: var(--bad); padding: 8px 12px; border-radius: 6px; }
  .aviso.suave { background: var(--unk-bg); color: var(--unk); }
  .estado { font-weight: 600; }
  .estado.listo { color: var(--ok); }
  .estado.error, .estado.sin_pausar { color: var(--bad); }
  @media (max-width: 560px) { .ficha { grid-template-columns: 1fr; gap: 2px; } .ficha dd { margin-bottom: 8px; } }
</style>
