<script lang="ts">
  import { api, fmt, nombreCampo, nombreEstrato, pct } from "./api";

  interface Fila {
    estrato: string; total: number; revisados: number; correctos: number; incorrectos: number; no_se_sabe: number;
    pendientes: number; precision: number | null; ic95: [number | null, number | null];
    requests_estrato: number; requests_probablemente_mal: number | null;
  }
  let datos = $state<any>(null);
  let error = $state("");
  let fuente = $state("conjunto");

  api("/api/admin/resumen").then(d => (datos = d)).catch(e => (error = e.message));

  const tabla = $derived<Fila[]>(!datos ? [] : fuente === "conjunto"
    ? datos.conjunto : datos.usuarios.find((u: any) => String(u.id) === fuente)?.precision ?? []);
  let masStats = $state(false);

  // Vista simple: una fila por campo, con la precisión de lo llenado (el vendedor no mandó nada)
  // y de lo corregido (el vendedor mandó otro valor). Se juntan los métodos de cada campo.
  interface Cuenta { ok: number; mal: number }
  const precisionDe = (c: Cuenta) => (c.ok + c.mal ? c.ok / (c.ok + c.mal) : null);
  const resumen = $derived.by(() => {
    const campos = new Map<string, { llenado: Cuenta; corregido: Cuenta; hayLlenado: boolean; hayCorregido: boolean }>();
    for (const e of tabla) {
      const [campo, metodo] = e.estrato.split("|");
      if (!metodo) continue;                      // la pregunta de la ficha IMDb no es un campo
      const c = campos.get(campo) ?? { llenado: { ok: 0, mal: 0 }, corregido: { ok: 0, mal: 0 }, hayLlenado: false, hayCorregido: false };
      const esCorregido = metodo.startsWith("corregido");
      const cuenta = esCorregido ? c.corregido : c.llenado;
      cuenta.ok += e.correctos;
      cuenta.mal += e.incorrectos;
      if (esCorregido) c.hayCorregido = true; else c.hayLlenado = true;
      campos.set(campo, c);
    }
    return [...campos].map(([campo, c]) => ({ campo, ...c }));
  });

  const fecha = (s: string | null) => (s ? new Date(s).toLocaleString("es-MX", { dateStyle: "medium", timeStyle: "short" }) : "—");
</script>

<main class="wrap">
  <h1>Resultados</h1>
  {#if error}<div class="aviso">{error}</div>{/if}
  {#if datos}
    <div class="usuarios">
      {#each datos.usuarios as u (u.id)}
        <div class="usuario">
          <div class="nombre"><b>{u.nombre}</b> <span class="rol">{u.usuario} · {u.rol}</span></div>
          <div class="pista"><div class="lleno" style="width: {(100 * u.muestra.hechos) / u.muestra.total}%"></div></div>
          <small>Muestra: {fmt(u.muestra.hechos)} de {fmt(u.muestra.total)} valores · {u.muestra.tarjetas_revisadas} de {u.muestra.tarjetas} tarjetas</small>
          <small>Fuera de la muestra: {fmt(u.completo.etiquetas)} valores etiquetados</small>
          <small>Banderas: {fmt(u.banderas.original_mal)} valores del vendedor mal · {fmt(u.banderas.previo_correcto)} «lo correcto era lo de antes»</small>
          <small>Última actividad: {fecha(u.ultima)}</small>
          <div class="descargas">
            <a href="/api/admin/exportar?usuario={u.id}&ambito=muestra" download>JSON muestra</a>
            {#if u.completo.etiquetas}<a href="/api/admin/exportar?usuario={u.id}&ambito=completo" download>JSON fuera de la muestra</a>{/if}
          </div>
        </div>
      {/each}
    </div>
    <p class="nota">El JSON de la muestra tiene el mismo formato que exportaba la página anterior: sirve tal cual para
      <code>scripts/calcular_precision_revision.py</code>.</p>

    <h2>Precisión por campo (muestra)</h2>
    <div class="filtros">
      <select bind:value={fuente}>
        <option value="conjunto">Todos los revisores (primer veredicto de cada valor)</option>
        {#each datos.usuarios as u}<option value={String(u.id)}>{u.nombre}</option>{/each}
      </select>
      <small>{datos.acuerdo.valores
        ? `Acuerdo entre revisores: ${pct(datos.acuerdo.acuerdo)} en ${fmt(datos.acuerdo.valores)} valores revisados por dos o más personas.`
        : "Todavía no hay valores revisados por dos personas."}</small>
    </div>
    <button class="interruptor" role="switch" aria-checked={masStats} onclick={() => (masStats = !masStats)}>
      <span class="riel"><span class="perilla"></span></span> Ver más stats
    </button>
    {#if !masStats}
      <div class="scroll simple">
        <table>
          <thead><tr><th>Campo</th><th>Precisión de lo llenado</th><th>Precisión de lo corregido</th></tr></thead>
          <tbody>
            {#each resumen as r (r.campo)}
              <tr>
                <td>{nombreCampo(r.campo)}</td>
                <td>{#if r.hayLlenado}<b>{pct(precisionDe(r.llenado))}</b>{:else}<span class="na">no aplica</span>{/if}</td>
                <td>{#if r.hayCorregido}<b>{pct(precisionDe(r.corregido))}</b>{:else}<span class="na">no aplica</span>{/if}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      <p class="nota">Llenado = el vendedor no mandó el dato y lo pusimos. Corregido = el vendedor mandó un valor y lo reemplazamos. Precisión = correctos / (correctos + incorrectos) de lo ya revisado, juntando los métodos de cada campo; «—» significa que aún no hay nada revisado.</p>
    {:else}
    <div class="scroll">
      <table>
        <thead><tr><th>Campo · método</th><th>Revisados</th><th>No se sabe</th><th>Pendientes</th><th>Precisión</th><th>IC 95%</th><th>Requests del estrato</th><th>Requests probablemente mal</th></tr></thead>
        <tbody>
          {#each tabla as e (e.estrato)}
            <tr>
              <td>{nombreEstrato(e.estrato)}</td>
              <td>{e.revisados}</td><td>{e.no_se_sabe}</td><td>{e.pendientes}</td>
              <td><b>{pct(e.precision)}</b></td>
              <td>{e.precision === null ? "—" : `${pct(e.ic95[0])}–${pct(e.ic95[1])}`}</td>
              <td>{e.requests_estrato ? fmt(e.requests_estrato) : "—"}</td>
              <td>{e.requests_probablemente_mal === null ? "—" : fmt(e.requests_probablemente_mal)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    <p class="nota">Precisión = correctos / (correctos + incorrectos), con intervalo de Wilson al 95 %. «No se sabe» no cuenta. Requests probablemente mal = (1 − precisión) × requests del estrato en el consolidado.</p>
    {/if}
  {:else if !error}
    <p>Cargando…</p>
  {/if}
</main>

<style>
  main { padding: 16px; }
  h1 { font-size: 20px; margin: 4px 0 14px; }
  h2 { font-size: 17px; margin: 24px 0 10px; }
  .usuarios { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
  .usuario { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; display: grid; gap: 4px; }
  .usuario small { color: var(--ink2); }
  .rol { color: var(--ink2); font-size: 12px; }
  .pista { height: 8px; background: var(--line); border-radius: 4px; overflow: hidden; margin: 4px 0; }
  .lleno { height: 100%; background: var(--ok); }
  .descargas { display: flex; gap: 12px; flex-wrap: wrap; font-size: 13px; margin-top: 4px; }
  .nota { color: var(--ink2); font-size: 13px; }
  .filtros { display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; margin-bottom: 10px; color: var(--ink2); }
  .scroll { overflow-x: auto; background: var(--card); border: 1px solid var(--line); border-radius: 10px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; font-variant-numeric: tabular-nums; }
  th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
  th:first-child, td:first-child { text-align: left; white-space: normal; min-width: 200px; }
  th { color: var(--ink2); font-weight: 600; }
  tr:last-child td { border-bottom: 0; }
  .simple { max-width: 640px; }
  .na { color: var(--empty); font-style: italic; }
  .interruptor { display: inline-flex; align-items: center; gap: 8px; margin-bottom: 10px; border: 0; background: none; padding: 2px 0; color: var(--ink); }
  .riel { width: 38px; height: 22px; border-radius: 11px; background: var(--empty); position: relative; transition: background .15s; flex: 0 0 auto; }
  .perilla { position: absolute; top: 2px; left: 2px; width: 18px; height: 18px; border-radius: 50%; background: #fff; transition: transform .15s; box-shadow: 0 1px 2px rgba(0, 0, 0, .3); }
  .interruptor[aria-checked="true"] .riel { background: var(--accent); }
  .interruptor[aria-checked="true"] .perilla { transform: translateX(16px); }
  .aviso { background: var(--bad-bg); color: var(--bad); padding: 8px 12px; border-radius: 6px; }
</style>
