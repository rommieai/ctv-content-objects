<script lang="ts">
  import { api, fmt } from "./api";

  interface Valor { valor: string; requests: number; paises: Record<string, number>; nombre?: string }
  interface Medida { filas: number; requests: number; pct_universo: number; pct_vendido: number | null; ecpm: number | null }
  // Señal de contenido que solo existe en PubMatic (el reporte no la trae): va al deal, no cambia los números
  interface SenalPm { nombre: string; es: string; ayuda: string; opciones?: [string, string][] }
  interface Extra { senal: string; operador: "is" | "contains" | "is any"; valores: string[] }
  interface SenalRegla { nombre: string; modo: "manual" | "estandar"; operador: string; valores: string[] }
  // Los content objects del reporte por los que se filtra, más búsqueda por título y señales solo-PubMatic
  interface FiltroDeal {
    paises: string[]; genero: string; categoria: string; serie?: string; rating?: string; duracion?: string; envivo?: string;
    idioma?: string; con_titulo?: string; titulo?: string; extras?: Extra[];
  }
  interface OpcionesDeals {
    meta: Record<string, string>; paises: { pais: string; requests: number }[]; generos: Valor[]; categorias: Valor[];
    atributos?: Record<string, Valor[]>; enriquecibles?: string[]; senales_pubmatic?: SenalPm[]; max_senales?: number;
    pubmatic: { configurado: boolean; dsp: string; buyer: string; ensayo: boolean };
  }
  interface Simulacion {
    filtro: FiltroDeal; senales?: SenalRegla[];
    universo: Medida; nativo: Medida; recomendado: Medida; lista: Medida; solo_lista: Medida; solo_nativo: Medida;
    titulos: { total: number; en_csv: number; requests_en_csv: number; bytes_csv: number;
      top: { titulo: string; requests: number; pct_vendido: number | null; ecpm: number | null }[] };
    publishers: { publisher: string; recomendado: Medida; nativo: Medida }[];
  }
  // Condiciones comerciales del deal: lo que se llena en el paso Configuration de PubMatic. Montos en USD.
  interface Condiciones {
    inicio: string; fin: string; fee: "no" | "fijo" | "porcentaje"; feeValor: number;
    subasta: "first" | "fixed"; mediaCpm: number | null;
  }
  interface Trabajo {
    id: number; nombre: string; estado: "en_cola" | "corriendo" | "listo" | "error" | "sin_pausar"; detalle: string;
    pm_id: string; enlace: string; titulos: number; creado: string; de: string;
    filtro: FiltroDeal;
    condiciones: Condiciones | null; resumen_pm: string;
  }

  let opciones = $state<OpcionesDeals | null>(null);
  let error = $state("");
  let paises = $state<string[]>(["Mexico"]);
  let genero = $state("");
  let categoria = $state("");
  let serie = $state("");
  let rating = $state("");
  let duracion = $state("");
  let envivo = $state("");
  let idioma = $state("");
  let conTitulo = $state("");
  let titulo = $state("");
  // señales solo-PubMatic: una fila por señal; los valores se escriben separados por coma
  let extras = $state<{ senal: string; operador: Extra["operador"]; texto: string }[]>([]);
  let sim = $state<Simulacion | null>(null);
  let calculando = $state(false);
  let nombre = $state("");
  let confirmo = $state(false);
  // condiciones del deal (paso Configuration de PubMatic)
  let inicio = $state("");
  let fin = $state("");
  let sinFin = $state(true);
  let fee = $state<Condiciones["fee"]>("no");
  let feeValor = $state<number | null>(null);
  let subasta = $state<Condiciones["subasta"]>("first");
  let mediaCpm = $state<number | null>(null);
  let creando = $state(false);
  let errorCrear = $state("");
  let trabajos = $state<Trabajo[]>([]);

  const TOP = 10;   // filas que se muestran en «Por dónde se vende» y en los títulos de la lista
  const pc = (x: number | null | undefined) => (x === null || x === undefined ? "—" : `${(100 * x).toFixed(1)}%`);
  const usd = (x: number | null | undefined) => (x === null || x === undefined ? "—" : `$${x.toFixed(2)}`);
  const fecha = (s: string) => new Date(s).toLocaleString("es-MX", { dateStyle: "medium", timeStyle: "short" });
  const enPaises = (v: Valor) => paises.some(p => v.paises[p]);
  const partir = (t: string) => [...new Set(t.split(/[,\n]/).map(x => x.trim()).filter(Boolean))];
  const extrasListos = (): Extra[] => extras.filter(e => e.senal && (e.operador === "is any" || partir(e.texto).length))
    .map(e => ({ senal: e.senal, operador: e.operador, valores: e.operador === "is any" ? [] : partir(e.texto) }));
  const filtro = (): FiltroDeal => ({
    paises, genero, categoria, serie: serie.trim(), rating, duracion, envivo, idioma, con_titulo: conTitulo, titulo: titulo.trim(), extras: extrasListos(),
  });
  // misma forma sin importar el orden de las llaves, para saber si lo calculado sigue correspondiendo a lo elegido
  const CAMPOS_FILTRO = ["genero", "categoria", "serie", "rating", "duracion", "envivo", "idioma", "con_titulo", "titulo"] as const;
  const clave = (f: FiltroDeal) => JSON.stringify([f.paises, CAMPOS_FILTRO.map(k => f[k] ?? ""), (f.extras ?? []).map(e => [e.senal, e.operador, e.valores])]);
  const SENAL_PM: Record<string, string> = {
    genero: "Genre", categoria: "Category", serie: "Series", rating: "Content Rating", duracion: "Length", envivo: "Live Stream",
    idioma: "Language", con_titulo: "Title present",
  };
  const NOMBRE_CAMPO: Record<string, string> = {
    genero: "Género", categoria: "Categoría IAB", serie: "Serie", rating: "Clasificación", duracion: "Duración", envivo: "En vivo",
    idioma: "Idioma", con_titulo: "Trae título", titulo: "Título contiene",
  };
  /** Los filtros del reporte como los pondría alguien a mano en PubMatic. */
  const comoNativo = (f: FiltroDeal) => [
    ...CAMPOS_FILTRO.filter(k => k !== "titulo" && f[k]).map(k => `${SENAL_PM[k]} is ${k === "genero" ? mayus(f[k]!) : f[k]}`),
    ...(f.titulo ? [`Title contains ${f.titulo}`] : []),
  ].join(" y ");
  const textoFiltro = (f: FiltroDeal) => [
    ...CAMPOS_FILTRO.filter(k => f[k]).map(k => `${NOMBRE_CAMPO[k]}: ${k === "genero" ? mayus(f[k]!) : f[k]}`),
    f.paises.join(", "), ...(f.extras ?? []).map(e => `${e.senal} ${e.operador}${e.valores.length ? " " + e.valores.join(", ") : ""}`),
  ].join(" · ");
  const esPm = (x: string) => opciones?.senales_pubmatic?.find(y => y.nombre === x);
  const valoresDe = (tipo: string) => (opciones?.atributos?.[tipo] ?? []).filter(enPaises);
  const etiquetaValor = (v: Valor) => (v.nombre ? v.nombre : v.valor);
  const mayus = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
  const ESTADO: Record<Trabajo["estado"], string> = {
    en_cola: "En cola", corriendo: "Creando…", listo: "Creado, en pausa", error: "Falló", sin_pausar: "Creado pero SIN PAUSAR",
  };

  const generos = $derived(opciones?.generos.filter(enPaises) ?? []);
  const categorias = $derived(opciones?.categorias.filter(enPaises) ?? []);
  const algunFiltro = $derived(!!(genero || categoria || serie.trim() || rating || duracion || envivo || idioma || conTitulo || titulo.trim().length >= 3));
  const listo = $derived(paises.length > 0 && algunFiltro);
  // lo que se calculó ya no corresponde a lo que está elegido
  const viejo = $derived(!!sim && clave(sim.filtro) !== clave(filtro()));
  // PubMatic admite pocas señales en la regla que acompaña a la lista de títulos, y el idioma ocupa una
  const cupoExtras = $derived((opciones?.max_senales ?? 3) - (idioma ? 1 : 0));
  const extraIncompleto = $derived(extras.some(e => !e.senal || (e.operador !== "is any" && !partir(e.texto).length)));
  const ganancia = $derived(sim && sim.nativo.requests ? sim.recomendado.requests / sim.nativo.requests - 1 : null);
  const activos = $derived(trabajos.some(t => t.estado === "en_cola" || t.estado === "corriendo"));
  const positivo = (x: number | null) => typeof x === "number" && x > 0;
  // por qué no se puede crear todavía con las condiciones escritas ("" = todo bien)
  const faltaCondicion = $derived(
    fee !== "no" && !positivo(feeValor) ? "Escribe el valor del transaction fee."
    : fee === "porcentaje" && (feeValor ?? 0) > 100 ? "El transaction fee en porcentaje no puede pasar de 100."
    : subasta === "fixed" && !positivo(mediaCpm) ? "Fixed Price necesita un Media CPM."
    : mediaCpm !== null && !positivo(mediaCpm) ? "El Media CPM debe ser mayor que 0."
    : !sinFin && !fin ? "Elige la fecha de fin o marca «Sin fecha de fin»."
    : !sinFin && fin && inicio && fin < inicio ? "La fecha de fin debe ser posterior a la de inicio."
    : "");
  const condiciones = (): Condiciones => ({
    inicio, fin: sinFin ? "" : fin, fee, feeValor: fee === "no" ? 0 : feeValor ?? 0, subasta, mediaCpm: positivo(mediaCpm) ? mediaCpm : null,
  });
  const dia = (iso: string) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}/${iso.slice(0, 4)}`;
  function textoCondiciones(c: Condiciones) {
    return [
      c.subasta === "fixed" ? `Fixed Price · Media CPM ${usd(c.mediaCpm)}` : c.mediaCpm ? `First Price · piso ${usd(c.mediaCpm)}` : "First Price",
      c.fee === "no" ? "sin fee" : c.fee === "fijo" ? `fee ${usd(c.feeValor)} CPM` : `fee ${c.feeValor}%`,
      `${c.inicio ? dia(c.inicio) : "desde hoy"} → ${c.fin ? dia(c.fin) : "sin fin"}`,
    ].join(" · ");
  }

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
      const hecho = sim;
      nombre = [...CAMPOS_FILTRO.map(k => hecho.filtro[k]), ...hecho.filtro.paises].filter(Boolean).join("-")
        .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80) + "-v" + (opciones?.meta.version ?? "");
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
      await api("/api/admin/deals/crear", { metodo: "POST", cuerpo: { ...sim!.filtro, nombre, condiciones: condiciones(), confirmo: true } });
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
      <h3 class="sub">Content objects del reporte</h3>
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
        {#if opciones.atributos}
          <label class="campo"><span class="etq">Serie</span>
            <input type="text" list="deals-series" bind:value={serie} placeholder="(cualquiera) — escribe para buscar" />
            <datalist id="deals-series">{#each valoresDe("serie").slice(0, 400) as v (v.valor)}<option value={v.valor}></option>{/each}</datalist>
          </label>
          <label class="campo"><span class="etq">Clasificación (rating)</span>
            <select bind:value={rating}>
              <option value="">(cualquiera)</option>
              {#each valoresDe("rating") as v (v.valor)}<option value={v.valor}>{v.valor}</option>{/each}
            </select>
          </label>
          <label class="campo"><span class="etq">Duración (código del reporte)</span>
            <select bind:value={duracion}>
              <option value="">(cualquiera)</option>
              {#each [...valoresDe("duracion")].sort((a, b) => a.valor.localeCompare(b.valor)) as v (v.valor)}<option value={v.valor}>Código {v.valor}</option>{/each}
            </select>
          </label>
          <label class="campo"><span class="etq">En vivo</span>
            <select bind:value={envivo}>
              <option value="">(cualquiera)</option>
              {#each valoresDe("envivo") as v (v.valor)}<option value={v.valor}>{etiquetaValor(v)}</option>{/each}
            </select>
          </label>
          <label class="campo"><span class="etq">Idioma <i>solo lo declarado</i></span>
            <select bind:value={idioma}>
              <option value="">(cualquiera)</option>
              {#each valoresDe("idioma") as v (v.valor)}<option value={v.valor}>{v.valor}</option>{/each}
            </select>
          </label>
          <label class="campo"><span class="etq">Trae título <i>solo lo declarado</i></span>
            <select bind:value={conTitulo}>
              <option value="">(cualquiera)</option>
              {#each valoresDe("con_titulo") as v (v.valor)}<option value={v.valor}>{etiquetaValor(v)}</option>{/each}
            </select>
          </label>
          <label class="campo"><span class="etq">Título contiene</span>
            <input type="text" bind:value={titulo} maxlength="80" placeholder="(cualquiera) — mínimo 3 letras" />
          </label>
        {/if}
      </div>

      {#if opciones.senales_pubmatic}
        <h3 class="sub">Otras señales</h3>
        {#each extras as e, i (i)}
          {@const def = esPm(e.senal)}
          <div class="extra">
            <select bind:value={e.senal} onchange={() => { e.texto = ""; e.operador = "is"; }}>
              <option value="">Elige una señal…</option>
              {#each opciones.senales_pubmatic as sp (sp.nombre)}
                <option value={sp.nombre} disabled={extras.some((x, j) => j !== i && x.senal === sp.nombre)}>{sp.es} ({sp.nombre})</option>
              {/each}
            </select>
            <select bind:value={e.operador} disabled={!e.senal}>
              <option value="is">is</option>
              {#if !def?.opciones}<option value="contains">contains</option>{/if}
              <option value="is any">is any (con cualquier valor)</option>
            </select>
            {#if e.operador === "is any"}
              <span class="nota">basta con que la señal venga en el request</span>
            {:else if def?.opciones}
              <select bind:value={e.texto}>
                <option value="">Elige…</option>
                {#each def.opciones as [cod, txt] (cod)}<option value={cod}>{txt} ({cod})</option>{/each}
              </select>
            {:else}
              <input type="text" bind:value={e.texto} disabled={!e.senal} placeholder={def?.ayuda ? `${def.ayuda}; varios separados por coma` : "valores separados por coma"} />
            {/if}
            <button type="button" onclick={() => (extras = extras.filter((_, j) => j !== i))}>Quitar</button>
          </div>
        {/each}
        <div><button type="button" disabled={extras.length >= cupoExtras} onclick={() => (extras = [...extras, { senal: "", operador: "is", texto: "" }])}>Agregar señal de PubMatic</button>
          <small class="nota">Máximo {opciones.max_senales ?? 3} en total{idioma ? " (el idioma ya ocupa una)" : ""}: es lo que PubMatic admite en una regla.</small></div>
        {#if extras.length}
          <small class="nota">El reporte no trae estas señales, así que no se puede saber cuánto inventario las cumple: la comparación no las cuenta
            y el deal real alcanzará <b>menos</b> de lo que se muestra. En PubMatic van todas en una segunda regla, unidas entre sí y a la lista de títulos con «y».</small>
        {/if}
      {/if}

      <button class="primario" disabled={!listo || calculando || extraIncompleto || extras.length > cupoExtras} onclick={comparar}>{calculando ? "Calculando…" : "Comparar"}</button>
      {#if !listo}<small class="nota">Elige al menos un país y un content object del reporte.</small>
      {:else if extraIncompleto}<small class="nota">Completa o quita la señal de PubMatic que quedó a medias.</small>
      {:else if extras.length > cupoExtras}<small class="nota falta">Hay más señales de las que PubMatic admite junto al idioma: quita una.</small>{/if}
    </section>

    {#if sim}
      <section class="caja" class:viejo>
        <h2>2. Qué habría pasado con cada camino</h2>
        {#if viejo}<div class="aviso suave">Cambiaste los filtros: vuelve a dar clic en Comparar.</div>{/if}
        <div class="caminos">
          <div class="camino">
            <h3>Con los filtros de PubMatic</h3>
            <p class="como">{comoNativo(sim.filtro)}: solo entra lo que el publisher declara.</p>
            <div class="grande">{fmt(sim.nativo.requests)}</div>
            <small>requests · {pc(sim.nativo.pct_universo)} de {sim.filtro.paises.join(", ")}</small>
            <dl><dt>Vendido</dt><dd>{pc(sim.nativo.pct_vendido)}</dd><dt>eCPM histórico</dt><dd>{usd(sim.nativo.ecpm)}</dd></dl>
          </div>
          <div class="camino recomendado">
            <h3>Con nuestra recomendación</h3>
            <p class="como">Lo mismo que alcanzan los filtros, más Title is [{fmt(sim.titulos.en_csv)} títulos que nuestra base clasifica así]:
              entra lo que el publisher declara y también lo que no declara.</p>
            <div class="grande">{fmt(sim.recomendado.requests)}</div>
            <small>requests · {pc(sim.recomendado.pct_universo)} de {sim.filtro.paises.join(", ")}
              {#if ganancia !== null}· <b class={ganancia >= 0 ? "sube" : "baja"}>{ganancia >= 0 ? "+" : ""}{(100 * ganancia).toFixed(0)}%</b> contra los filtros{/if}</small>
            <dl><dt>Vendido</dt><dd>{pc(sim.recomendado.pct_vendido)}</dd><dt>eCPM histórico</dt><dd>{usd(sim.recomendado.ecpm)}</dd></dl>
          </div>
        </div>
        <ul class="nota lista">
          <li>La lista de títulos alcanza {fmt(sim.lista.requests)} requests; {fmt(sim.solo_lista.requests)} de ellos no los ven los filtros
            (eCPM histórico {usd(sim.solo_lista.ecpm)}): eso es lo que la recomendación agrega.</li>
          <li>Los filtros alcanzan {fmt(sim.solo_nativo.requests)} requests que la lista no cubre, casi siempre porque vienen sin título.
            También cuentan en la recomendación.</li>
          <li>En PubMatic dos reglas de contenido se unen con «y», así que la recomendación completa son <b>dos deals</b>: uno con la lista de
            títulos (el que se crea abajo) y otro con los filtros de PubMatic.</li>
          {#if sim.titulos.total > sim.titulos.en_csv}
            <li>La lista tiene {fmt(sim.titulos.total)} títulos; al CSV solo le caben {fmt(sim.titulos.en_csv)} (tope de PubMatic), los de más requests.</li>
          {/if}
          <li>El eCPM es lo que se pagó en esa ventana, no el precio de tu deal: ese lo fijas en PubMatic.</li>
        </ul>

        <h3>Por dónde se vende</h3>
        <div class="scroll">
          <table>
            <thead><tr><th>Publisher</th><th>Requests de la recomendación</th><th>% de la recomendación</th><th>Vendido</th><th>eCPM histórico</th></tr></thead>
            <tbody>
              {#each sim.publishers.filter(p => p.recomendado.requests).slice(0, TOP) as p (p.publisher)}
                <tr><td>{p.publisher}</td><td>{fmt(p.recomendado.requests)}</td><td>{pc(p.recomendado.pct_universo)}</td>
                  <td>{pc(p.recomendado.pct_vendido)}</td><td>{usd(p.recomendado.ecpm)}</td></tr>
              {/each}
            </tbody>
          </table>
        </div>

        <h3>Títulos con más requests de la lista</h3>
        <div class="scroll">
          <table>
            <thead><tr><th>Título</th><th>Requests</th><th>Vendido</th><th>eCPM histórico</th></tr></thead>
            <tbody>
              {#each sim.titulos.top.slice(0, TOP) as t (t.titulo)}
                <tr><td>{t.titulo}</td><td>{fmt(t.requests)}</td><td>{pc(t.pct_vendido)}</td><td>{usd(t.ecpm)}</td></tr>
              {/each}
            </tbody>
          </table>
        </div>
      </section>

      <section class="caja" class:viejo>
        <h2>3. Llevar la recomendación a PubMatic</h2>
        <p class="nota">Se crea un Auction Package Deal con {opciones.pubmatic.dsp} · {opciones.pubmatic.buyer}, video en CTV,
          {sim.filtro.paises.join(", ")} y la regla Title is con {fmt(sim.titulos.en_csv)} títulos ({fmt(sim.lista.requests)} requests de la
          recomendación; los otros {fmt(sim.solo_nativo.requests)} piden un segundo deal con los filtros de PubMatic). Las condiciones de abajo
          se llenan tal cual en PubMatic. <b>Queda en pausa</b>: la activación la decides tú en PubMatic.</p>
        {#if sim.senales?.length}
          <p class="nota">Además lleva una segunda regla de contenido, unida a la de títulos con «y»:
            <b>{sim.senales.map(x => `${x.nombre} ${x.operador}${x.valores.length ? " " + x.valores.join(", ") : ""}`).join(" y ")}</b>.
            {#if sim.filtro.extras?.length}Las señales que no están en el reporte no se cuentan en la comparación: el deal alcanzará menos de lo que se muestra arriba.{/if}</p>
        {/if}
        <div class="crear">
          <label class="campo"><span class="etq">Nombre del deal</span><input type="text" bind:value={nombre} maxlength="100" /></label>

          <fieldset>
            <legend>Transaction Date</legend>
            <div class="linea">
              <label class="campo"><span class="etq">Desde</span><input type="date" bind:value={inicio} /></label>
              <label class="campo"><span class="etq">Hasta</span><input type="date" bind:value={fin} min={inicio || undefined} disabled={sinFin} /></label>
              <label class="marca"><input type="checkbox" bind:checked={sinFin} /> Sin fecha de fin (Ongoing)</label>
            </div>
            <small class="nota">Sin «Desde», el deal arranca hoy. PubMatic usa hora del Pacífico.</small>
          </fieldset>

          <fieldset>
            <legend>Transaction Fee</legend>
            <div class="linea">
              <div class="opciones">
                <button type="button" class:sel={fee === "no"} onclick={() => (fee = "no")}>No</button>
                <button type="button" class:sel={fee !== "no"} onclick={() => { if (fee === "no") fee = "fijo"; }}>Sí</button>
              </div>
              {#if fee !== "no"}
                <div class="campo"><span class="etq">CPM</span>
                  <div class="opciones">
                    <button type="button" class:sel={fee === "fijo"} onclick={() => (fee = "fijo")}>Fixed</button>
                    <button type="button" class:sel={fee === "porcentaje"} onclick={() => (fee = "porcentaje")}>Percentage</button>
                  </div>
                </div>
                <label class="campo"><span class="etq">{fee === "fijo" ? "USD por mil" : "Porcentaje"}</span>
                  <span class="monto"><span>{fee === "fijo" ? "$" : "%"}</span>
                    <input type="number" bind:value={feeValor} min="0" max={fee === "fijo" ? undefined : 100} step="0.01" placeholder="0.00" /></span>
                </label>
              {/if}
            </div>
            {#if fee === "fijo"}<small class="nota">PubMatic admite hasta $10 de fee fijo.</small>{/if}
          </fieldset>

          <fieldset>
            <legend>Auction Type y Media CPM</legend>
            <div class="linea">
              <div class="opciones">
                <button type="button" class:sel={subasta === "first"} onclick={() => (subasta = "first")}>First Price</button>
                <button type="button" class:sel={subasta === "fixed"} onclick={() => (subasta = "fixed")}>Fixed Price</button>
              </div>
              <label class="campo"><span class="etq">{subasta === "fixed" ? "Media CPM (USD)" : "Piso de media, opcional (USD)"}</span>
                <span class="monto"><span>$</span>
                  <input type="number" bind:value={mediaCpm} min="0" step="0.01" placeholder={subasta === "fixed" ? "0.00" : "piso por defecto"} /></span>
              </label>
            </div>
            <small class="nota">{subasta === "fixed"
              ? "Fixed Price: el comprador paga exactamente ese Media CPM."
              : "First Price: gana la puja más alta. Sin piso, PubMatic usa el suyo por defecto ($0.50)."}</small>
          </fieldset>

          <p class="resumen-cond"><b>Se creará con:</b> {textoCondiciones(condiciones())}</p>
          {#if faltaCondicion}<small class="nota falta">{faltaCondicion}</small>{/if}
          <label class="confirmo"><input type="checkbox" bind:checked={confirmo} /> Entiendo que esto crea un deal real en la cuenta de PubMatic</label>
          <div class="botones">
            <button class="primario" disabled={viejo || creando || !confirmo || !nombre.trim() || !!faltaCondicion || !opciones.pubmatic.configurado || !sim.titulos.en_csv} onclick={crear}>
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
            <thead><tr><th>Deal</th><th>Filtros</th><th>Condiciones</th><th>Títulos</th><th>Estado</th><th>Quién</th><th>Cuándo</th></tr></thead>
            <tbody>
              {#each trabajos as t (t.id)}
                <tr>
                  <td>{#if t.enlace}<a href={t.enlace} target="_blank" rel="noopener">{t.nombre}</a>{:else}{t.nombre}{/if}
                    {#if t.pm_id}<br /><small>{t.pm_id}</small>{/if}</td>
                  <td class="izq">{textoFiltro(t.filtro)}</td>
                  <td class="izq">{t.condiciones ? textoCondiciones(t.condiciones) : "First Price · sin fee · sin fin"}</td>
                  <td>{fmt(t.titulos)}</td>
                  <td class="izq"><span class="estado {t.estado}">{ESTADO[t.estado]}</span>{#if t.estado !== "listo"}<br /><small>{t.detalle}</small>{/if}
                    {#if t.resumen_pm}<br /><small title="Lo que mostró el resumen de PubMatic">PubMatic: {t.resumen_pm.split(" · Auction Type · ")[1] ? "Auction Type · " + t.resumen_pm.split(" · Auction Type · ")[1] : t.resumen_pm}</small>{/if}</td>
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
  h3.sub { margin: 6px 0 0; }
  .etq i { font-style: normal; opacity: .7; font-size: 11px; margin-left: 4px; }
  .campo input[type=text], .campo select { width: 100%; }
  .extra { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) minmax(0, 2fr) auto; gap: 8px; align-items: center; }
  .extra input[type=text], .extra select { width: 100%; }
  @media (max-width: 720px) { .extra { grid-template-columns: 1fr; } }
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
  .camino.recomendado { border-color: var(--accent); background: var(--accent-bg); box-shadow: 0 0 20px 2px rgba(163, 87, 250, .2); }
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
  .crear { display: grid; gap: 12px; max-width: 680px; }
  .crear input[type=text] { width: 100%; }
  fieldset { border: 1px solid var(--line); border-radius: 10px; padding: 10px 14px 12px; margin: 0; display: grid; gap: 8px; min-width: 0; }
  legend { font-size: 13px; font-weight: 600; color: var(--ink2); padding: 0 6px; }
  .linea { display: flex; flex-wrap: wrap; gap: 10px 16px; align-items: end; }
  .opciones { display: flex; }
  .opciones button { border-radius: 0; padding: 6px 12px; font-size: 14px; }
  .opciones button:first-child { border-radius: 6px 0 0 6px; }
  .opciones button:last-child { border-radius: 0 6px 6px 0; margin-left: -1px; }
  .opciones button.sel { background: var(--accent-fuerte); border-color: var(--accent); color: #fff; font-weight: 600; }
  .crear input[type=date], .crear input[type=number] {
    font: inherit; padding: 6px 8px; border: 1px solid var(--line); border-radius: 6px; background: var(--card); color: var(--ink);
    min-width: 0; max-width: 100%;
  }
  .crear input[type=number] { width: 150px; font-variant-numeric: tabular-nums; }
  .crear input:disabled { opacity: .45; }
  .monto { display: flex; align-items: center; gap: 6px; color: var(--ink2); }
  .marca { display: flex; gap: 6px; align-items: center; font-size: 14px; padding-bottom: 6px; }
  .resumen-cond { margin: 0; font-size: 14px; }
  .falta { color: var(--bad); }
  .confirmo { display: flex; gap: 8px; align-items: center; font-size: 14px; }
  .botones { display: flex; flex-wrap: wrap; gap: 8px; }
  .aviso { background: var(--bad-bg); color: var(--bad); padding: 8px 12px; border-radius: 6px; }
  .aviso.suave { background: var(--unk-bg); color: var(--unk); }
  .estado { font-weight: 600; }
  .estado.listo { color: var(--ok); }
  .estado.error, .estado.sin_pausar { color: var(--bad); }
</style>
