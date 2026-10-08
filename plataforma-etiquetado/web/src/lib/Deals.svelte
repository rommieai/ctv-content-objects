<script lang="ts">
  import { api, fmt } from "./api";

  interface Valor { valor: string; requests: number; paises: Record<string, number>; nombre?: string }
  interface Medida { filas: number; requests: number; pct_universo: number; pct_vendido: number | null; ecpm: number | null }
  interface OpcionesDeals {
    meta: Record<string, string>; paises: { pais: string; requests: number }[]; generos: Valor[]; categorias: Valor[];
    pubmatic: { configurado: boolean; dsp: string; buyer: string; ensayo: boolean };
  }
  interface Simulacion {
    filtro: { paises: string[]; genero: string; categoria: string };
    universo: Medida; nativo: Medida; recomendado: Medida; union: Medida; solo_recomendado: Medida; solo_nativo: Medida;
    titulos: { total: number; en_csv: number; requests_en_csv: number; bytes_csv: number;
      top: { titulo: string; requests: number; pct_vendido: number | null; ecpm: number | null }[] };
    publishers: { publisher: string; recomendado: Medida; nativo: Medida }[];
  }
  interface Trabajo {
    id: number; nombre: string; estado: "en_cola" | "corriendo" | "listo" | "error" | "sin_pausar"; detalle: string;
    pm_id: string; enlace: string; titulos: number; creado: string; de: string;
    filtro: { paises: string[]; genero: string; categoria: string };
  }

  let opciones = $state<OpcionesDeals | null>(null);
  let error = $state("");
  let paises = $state<string[]>(["Mexico"]);
  let genero = $state("");
  let categoria = $state("");
  let sim = $state<Simulacion | null>(null);
  let calculando = $state(false);
  let nombre = $state("");
  let confirmo = $state(false);
  let creando = $state(false);
  let errorCrear = $state("");
  let trabajos = $state<Trabajo[]>([]);

  const pc = (x: number | null | undefined) => (x === null || x === undefined ? "—" : `${(100 * x).toFixed(1)}%`);
  const usd = (x: number | null | undefined) => (x === null || x === undefined ? "—" : `$${x.toFixed(2)}`);
  const fecha = (s: string) => new Date(s).toLocaleString("es-MX", { dateStyle: "medium", timeStyle: "short" });
  const enPaises = (v: Valor) => paises.some(p => v.paises[p]);
  const filtro = () => ({ paises, genero, categoria });
  const mayus = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
  const ESTADO: Record<Trabajo["estado"], string> = {
    en_cola: "En cola", corriendo: "Creando…", listo: "Creado, en pausa", error: "Falló", sin_pausar: "Creado pero SIN PAUSAR",
  };

  const generos = $derived(opciones?.generos.filter(enPaises) ?? []);
  const categorias = $derived(opciones?.categorias.filter(enPaises) ?? []);
  const listo = $derived(paises.length > 0 && (!!genero || !!categoria));
  // lo que se calculó ya no corresponde a lo que está elegido
  const viejo = $derived(!!sim && JSON.stringify(sim.filtro) !== JSON.stringify(filtro()));
  const ganancia = $derived(sim && sim.nativo.requests ? sim.recomendado.requests / sim.nativo.requests - 1 : null);
  const activos = $derived(trabajos.some(t => t.estado === "en_cola" || t.estado === "corriendo"));

  api<OpcionesDeals>("/api/admin/deals/opciones").then(o => (opciones = o)).catch(e => (error = e.message));
  const cargarTrabajos = () => api<{ trabajos: Trabajo[] }>("/api/admin/deals/trabajos").then(r => (trabajos = r.trabajos)).catch(() => {});
  cargarTrabajos();
  $effect(() => {
    if (!activos) return;
    const t = setInterval(cargarTrabajos, 4000);
    return () => clearInterval(t);
  });

  function alternar(p: string) {
    paises = paises.includes(p) ? paises.filter(x => x !== p) : [...paises, p];
  }
  async function comparar() {
    calculando = true; error = "";
    try {
      sim = await api<Simulacion>("/api/admin/deals/simular", { metodo: "POST", cuerpo: filtro() });
      nombre = [sim.filtro.genero, sim.filtro.categoria, ...sim.filtro.paises].filter(Boolean).join("-")
        .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") + "-v" + (opciones?.meta.version ?? "");
      confirmo = false; errorCrear = "";
    } catch (e) { error = (e as Error).message; }
    calculando = false;
  }
  async function descargar() {
    const r = await fetch("/api/admin/deals/titulos.csv", {
      method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify(sim!.filtro),
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(await r.blob());
    a.download = `Title_is-${nombre || "deal"}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }
  async function crear() {
    creando = true; errorCrear = "";
    try {
      await api("/api/admin/deals/crear", { metodo: "POST", cuerpo: { ...sim!.filtro, nombre, confirmo: true } });
      confirmo = false;
      await cargarTrabajos();
    } catch (e) { errorCrear = (e as Error).message; }
    creando = false;
  }
</script>

<main class="wrap">
  <h1>Armador de deals</h1>
  {#if error}<div class="aviso">{error}</div>{/if}
  {#if opciones}
    <p class="nota">Datos del corte v{opciones.meta.version} ({opciones.meta.ventana}), {fmt(+opciones.meta.requests)} requests.
      Todo lo que se muestra es histórico: lo que pasó en esa ventana, no una promesa de lo que va a pasar.</p>

    <section class="caja">
      <h2>1. ¿Qué inventario quieres?</h2>
      <div class="campo">
        <span class="etq">Países</span>
        <div class="chips">
          {#each opciones.paises.slice(0, 12) as p (p.pais)}
            <button class:sel={paises.includes(p.pais)} onclick={() => alternar(p.pais)}>{p.pais}</button>
          {/each}
        </div>
      </div>
      <div class="dos">
        <label class="campo"><span class="etq">Género</span>
          <select bind:value={genero}>
            <option value="">(cualquiera)</option>
            {#each generos as g (g.valor)}<option value={g.valor}>{mayus(g.valor)}</option>{/each}
          </select>
        </label>
        <label class="campo"><span class="etq">Categoría IAB</span>
          <select bind:value={categoria}>
            <option value="">(cualquiera)</option>
            {#each categorias as c (c.valor)}<option value={c.valor}>{c.valor}{c.nombre ? ` · ${c.nombre}` : ""}</option>{/each}
          </select>
        </label>
      </div>
      <button class="primario" disabled={!listo || calculando} onclick={comparar}>{calculando ? "Calculando…" : "Comparar"}</button>
      {#if !listo}<small class="nota">Elige al menos un país y un género o una categoría.</small>{/if}
    </section>

    {#if sim}
      <section class="caja" class:viejo>
        <h2>2. Qué habría pasado con cada camino</h2>
        {#if viejo}<div class="aviso suave">Cambiaste los filtros: vuelve a dar clic en Comparar.</div>{/if}
        <div class="caminos">
          <div class="camino">
            <h3>Con los filtros de PubMatic</h3>
            <p class="como">{[sim.filtro.genero && `Genre is ${mayus(sim.filtro.genero)}`, sim.filtro.categoria && `Category is ${sim.filtro.categoria}`].filter(Boolean).join(" y ")}:
              solo entra lo que el publisher declara.</p>
            <div class="grande">{fmt(sim.nativo.requests)}</div>
            <small>requests · {pc(sim.nativo.pct_universo)} de {sim.filtro.paises.join(", ")}</small>
            <dl><dt>Vendido</dt><dd>{pc(sim.nativo.pct_vendido)}</dd><dt>eCPM histórico</dt><dd>{usd(sim.nativo.ecpm)}</dd></dl>
          </div>
          <div class="camino recomendado">
            <h3>Con nuestra recomendación</h3>
            <p class="como">Title is [{fmt(sim.titulos.en_csv)} títulos que nuestra base clasifica así]: entra aunque el publisher no lo declare.</p>
            <div class="grande">{fmt(sim.recomendado.requests)}</div>
            <small>requests · {pc(sim.recomendado.pct_universo)} de {sim.filtro.paises.join(", ")}
              {#if ganancia !== null}· <b class={ganancia >= 0 ? "sube" : "baja"}>{ganancia >= 0 ? "+" : ""}{(100 * ganancia).toFixed(0)}%</b> contra los filtros{/if}</small>
            <dl><dt>Vendido</dt><dd>{pc(sim.recomendado.pct_vendido)}</dd><dt>eCPM histórico</dt><dd>{usd(sim.recomendado.ecpm)}</dd></dl>
          </div>
        </div>
        <ul class="nota lista">
          <li>La recomendación alcanza {fmt(sim.solo_recomendado.requests)} requests que los filtros no ven (eCPM histórico {usd(sim.solo_recomendado.ecpm)}).</li>
          <li>Los filtros alcanzan {fmt(sim.solo_nativo.requests)} requests que la lista no cubre, casi siempre porque vienen sin título.
            En PubMatic dos reglas de contenido se unen con «y», así que para tener los dos harían falta dos deals.</li>
          {#if sim.titulos.total > sim.titulos.en_csv}
            <li>La lista tiene {fmt(sim.titulos.total)} títulos; al CSV solo le caben {fmt(sim.titulos.en_csv)} (tope de PubMatic), los de más requests.</li>
          {/if}
          <li>El eCPM es lo que se pagó en esa ventana, no el precio de tu deal: ese lo fijas en PubMatic.</li>
        </ul>

        <h3>Por dónde se vende (el precio lo pone la ruta, no el título)</h3>
        <div class="scroll">
          <table>
            <thead><tr><th>Publisher</th><th>Requests de la recomendación</th><th>% de la recomendación</th><th>Vendido</th><th>eCPM histórico</th></tr></thead>
            <tbody>
              {#each sim.publishers.filter(p => p.recomendado.requests) as p (p.publisher)}
                <tr><td>{p.publisher}</td><td>{fmt(p.recomendado.requests)}</td><td>{pc(p.recomendado.pct_universo)}</td>
                  <td>{pc(p.recomendado.pct_vendido)}</td><td>{usd(p.recomendado.ecpm)}</td></tr>
              {/each}
            </tbody>
          </table>
        </div>

        <h3>Títulos con más requests de la lista</h3>
        <div class="scroll">
          <table>
            <thead><tr><th>Título (como llega en el bid request)</th><th>Requests</th><th>Vendido</th><th>eCPM histórico</th></tr></thead>
            <tbody>
              {#each sim.titulos.top as t (t.titulo)}
                <tr><td>{t.titulo}</td><td>{fmt(t.requests)}</td><td>{pc(t.pct_vendido)}</td><td>{usd(t.ecpm)}</td></tr>
              {/each}
            </tbody>
          </table>
        </div>
      </section>

      <section class="caja" class:viejo>
        <h2>3. Llevar la recomendación a PubMatic</h2>
        <p class="nota">Se crea un Auction Package Deal con {opciones.pubmatic.dsp} · {opciones.pubmatic.buyer}, video en CTV,
          {sim.filtro.paises.join(", ")} y la regla Title is con {fmt(sim.titulos.en_csv)} títulos. Sin transaction fee, First Price y el piso
          por defecto de PubMatic. <b>Queda en pausa</b>: el precio y la activación los decides tú en PubMatic.</p>
        <div class="crear">
          <label class="campo"><span class="etq">Nombre del deal</span><input type="text" bind:value={nombre} maxlength="100" /></label>
          <label class="confirmo"><input type="checkbox" bind:checked={confirmo} /> Entiendo que esto crea un deal real en la cuenta de PubMatic</label>
          <div class="botones">
            <button class="primario" disabled={viejo || creando || !confirmo || !nombre.trim() || !opciones.pubmatic.configurado || !sim.titulos.en_csv} onclick={crear}>
              {creando ? "Enviando…" : "Crear en PubMatic (en pausa)"}</button>
            <button disabled={viejo || !sim.titulos.en_csv} onclick={descargar}>Descargar el CSV de títulos</button>
          </div>
          {#if !opciones.pubmatic.configurado}<small class="nota">Este servidor no tiene las credenciales de PubMatic: puedes descargar el CSV y subirlo a mano en Content Object › Title › Upload.</small>{/if}
          {#if opciones.pubmatic.ensayo}<small class="nota">Servidor en modo ensayo: el bot recorre el asistente de PubMatic pero no crea el deal.</small>{/if}
          {#if errorCrear}<div class="aviso">{errorCrear}</div>{/if}
        </div>
      </section>
    {/if}

    {#if trabajos.length}
      <section class="caja">
        <h2>Deals creados desde aquí</h2>
        <div class="scroll">
          <table>
            <thead><tr><th>Deal</th><th>Filtros</th><th>Títulos</th><th>Estado</th><th>Quién</th><th>Cuándo</th></tr></thead>
            <tbody>
              {#each trabajos as t (t.id)}
                <tr>
                  <td>{#if t.enlace}<a href={t.enlace} target="_blank" rel="noopener">{t.nombre}</a>{:else}{t.nombre}{/if}
                    {#if t.pm_id}<br /><small>{t.pm_id}</small>{/if}</td>
                  <td class="izq">{[t.filtro.genero && mayus(t.filtro.genero), t.filtro.categoria, t.filtro.paises.join(", ")].filter(Boolean).join(" · ")}</td>
                  <td>{fmt(t.titulos)}</td>
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
  h2 { font-size: 17px; margin: 0 0 12px; }
  h3 { font-size: 14px; margin: 18px 0 8px; }
  .nota { color: var(--ink2); font-size: 13px; }
  .lista { margin: 12px 0 0; padding-left: 18px; display: grid; gap: 4px; }
  .caja { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 16px; margin-top: 14px; display: grid; gap: 12px; }
  .caja.viejo > :not(h2):not(.aviso) { opacity: .45; }
  .campo { display: grid; gap: 4px; min-width: 0; }
  .etq { font-size: 13px; color: var(--ink2); }
  .dos { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .chips button { padding: 3px 10px; font-size: 13px; }
  .chips button.sel { background: var(--accent); border-color: var(--accent); color: #fff; }
  .caja > button.primario { justify-self: start; }
  .caminos { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
  .camino { border: 1px solid var(--line); border-radius: 10px; padding: 14px; display: grid; gap: 4px; align-content: start; }
  .camino.recomendado { border-color: var(--fill-line); background: var(--fill-bg); }
  .camino h3 { margin: 0; }
  .como { margin: 0 0 8px; font-size: 13px; color: var(--ink2); }
  .grande { font-size: 26px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .camino small { color: var(--ink2); }
  .sube { color: var(--ok); } .baja { color: var(--bad); }
  dl { display: grid; grid-template-columns: auto 1fr; gap: 2px 12px; margin: 10px 0 0; font-size: 14px; }
  dt { color: var(--ink2); } dd { margin: 0; font-weight: 600; font-variant-numeric: tabular-nums; }
  .scroll { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; font-variant-numeric: tabular-nums; }
  th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
  th:first-child, td:first-child, td.izq { text-align: left; white-space: normal; }
  th { color: var(--ink2); font-weight: 600; }
  tr:last-child td { border-bottom: 0; }
  .crear { display: grid; gap: 10px; max-width: 560px; }
  .crear input[type=text] { width: 100%; }
  .confirmo { display: flex; gap: 8px; align-items: center; font-size: 14px; }
  .botones { display: flex; flex-wrap: wrap; gap: 8px; }
  .aviso { background: var(--bad-bg); color: var(--bad); padding: 8px 12px; border-radius: 6px; }
  .aviso.suave { background: var(--unk-bg); color: var(--unk); }
  .estado { font-weight: 600; }
  .estado.listo { color: var(--ok); }
  .estado.error, .estado.sin_pausar { color: var(--bad); }
</style>
