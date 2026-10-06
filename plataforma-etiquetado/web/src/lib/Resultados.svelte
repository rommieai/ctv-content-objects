<script lang="ts">
  import { api, fmt, nombreEstrato, pct } from "./api";

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

    <h2>Precisión por estrato (muestra)</h2>
    <div class="filtros">
      <select bind:value={fuente}>
        <option value="conjunto">Todos los revisores (primer veredicto de cada valor)</option>
        {#each datos.usuarios as u}<option value={String(u.id)}>{u.nombre}</option>{/each}
      </select>
      <small>{datos.acuerdo.valores
        ? `Acuerdo entre revisores: ${pct(datos.acuerdo.acuerdo)} en ${fmt(datos.acuerdo.valores)} valores revisados por dos o más personas.`
        : "Todavía no hay valores revisados por dos personas."}</small>
    </div>
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
  .aviso { background: var(--bad-bg); color: var(--bad); padding: 8px 12px; border-radius: 6px; }
</style>
