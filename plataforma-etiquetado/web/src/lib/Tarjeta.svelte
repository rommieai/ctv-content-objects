<script lang="ts">
  import { fmt, pendientesDe, type Campo, type Iab, type Registro } from "./api";
  import Botones from "./Botones.svelte";

  let { r, mostrarFila = false, onveredicto, oncorreccion, onnota }: {
    r: Registro; mostrarFila?: boolean;
    onveredicto: (r: Registro, campo: string, valor: string, v: string) => void;
    oncorreccion: (r: Registro, campo: string, valor: string, texto: string) => void;
    onnota: (r: Registro, texto: string) => void;
  } = $props();

  const pend = $derived(pendientesDe(r));
  const FICHA = "_ficha_externa";
  const ETIQ_EXTRA: [string, string][] = [["titulo_imdb", "Título en IMDb"], ["titulo_original", "Título original"], ["tipo", "Tipo"],
    ["anio_inicio", "Año"], ["anio_fin", "Año de fin (series)"], ["duracion_min", "Duración (min)"], ["generos_imdb", "Géneros IMDb"],
    ["calificacion", "Calificación IMDb"], ["confianza", "Confianza del match"]];
  const ETIQ_WD: [string, string][] = [["pais", "País de origen"], ["idioma_original", "Idioma original"], ["estreno", "Estreno"],
    ["director", "Dirección"], ["reparto", "Reparto"], ["productora", "Productora"], ["cadena", "Cadena original"],
    ["temporadas", "Temporadas"], ["episodios", "Episodios"], ["tmdb_pelicula", "ID TMDB (película)"], ["tmdb_serie", "ID TMDB (serie)"]];

  const iabDe = (c: Campo): Record<string, Iab> =>
    c.significado && "iab" in c.significado ? Object.fromEntries(c.significado.iab.map(x => [x.codigo, x])) : {};
  const texto = (c: Campo) => (c.significado && "texto" in c.significado ? c.significado.texto : "");
  const valorExtra = (k: string) => {
    const x = r.extra;
    if (k === "calificacion" && x.calificacion) return `${x.calificacion} / 10 (${fmt(+x.votos)} votos)`;
    return x[k];
  };
  const tituloFicha = $derived(r.extra
    ? [r.extra.titulo_imdb || r.extra.imdb_id, [r.extra.tipo, r.extra.anio_inicio].filter(Boolean).join(", ")].filter(Boolean).join(" — ")
    : "");
</script>

{#snippet iab(x: Iab, conCodigo: boolean)}
  <div class="sig">{#if conCodigo}<span class="cod">{x.codigo}</span> {/if}{x.es}
    {#if x.en && x.en !== x.es}<span class="en">({x.en}{x.tax ? " · " + x.tax : ""})</span>
    {:else if x.tax}<span class="en">({x.tax})</span>{/if}
  </div>
{/snippet}

<section class="tarjeta" class:completa={pend === 0} id="f{r.fila_id}">
  <div class="cabeza">
    <span class="num">{r.muestra_id !== null ? `#${r.muestra_id}` : `fila ${fmt(r.fila_id)}`}</span>
    <span class="titulo">{r.titulo || "(sin título)"}</span>
    {#if r.muestra_id !== null && mostrarFila}<span class="chip">EN LA MUESTRA</span>{/if}
    <span class="num">{pend === 0 ? "✓ revisada" : `${pend} pendiente${pend > 1 ? "s" : ""}`}</span>
    <div class="contexto">App: <b>{r.app || "—"}</b> · {r.publisher} · {r.pais} · {fmt(r.requests)} requests{r.bundle ? " · " + r.bundle : ""}</div>
    <div class="enlaces">
      <a href={r.ayuda.busqueda} target="_blank" rel="noopener">Buscar</a>
      {#if r.ayuda.imdb} · <a href={r.ayuda.imdb} target="_blank" rel="noopener">Ficha IMDb de referencia: {r.ayuda.imdb_texto}</a>{/if}
    </div>
  </div>

  <table>
    <tbody>
    {#each r.campos as c (c.campo)}
      {#if !c.llenado}
        <tr>
          <td class="campo">{c.nombre}</td>
          <td>
            <div class="original">
              <div class="que">
                {#if c.valor}<span class="valor">{c.valor}</span>{:else}<span class="vacio">vacío</span>{/if}
                {#if c.significado && "iab" in c.significado}{#each c.significado.iab as x}{@render iab(x, true)}{/each}
                {:else if texto(c)}<div class="sig">{texto(c)}</div>{/if}
              </div>
              {#if c.valor}
                {@const k = `_original:${c.campo}|${c.valor}`}
                <div class="acc">
                  <button class="bandera" class:activa={!!r.etiquetas[k]} title="Marca este valor del vendedor como incorrecto"
                    onclick={() => onveredicto(r, `_original:${c.campo}`, c.valor, r.etiquetas[k] ? "" : "incorrecto")}>⚑ Está mal</button>
                  {#if r.etiquetas[k]}
                    <input type="text" class="correccion" placeholder="valor correcto (opcional)" value={r.etiquetas[k].correcto}
                      oninput={ev => oncorreccion(r, `_original:${c.campo}`, c.valor, ev.currentTarget.value)} />
                  {/if}
                </div>
              {/if}
            </div>
          </td>
        </tr>
      {:else}
        {@const mapa = iabDe(c)}
        {@const varias = c.unidades.length > 1}
        <tr class="llenado" class:corregido={c.corregido}>
          <td class="campo">{c.nombre}<span class="etiqueta">{c.corregido ? "CORREGIDO" : "LLENADO"}</span>
            {#if varias}<div class="antes">{c.unidades.length} valores: juzga cada uno</div>{/if}
          </td>
          <td>
            {#each c.unidades as u (u.valor)}
              {@const k = `${c.campo}|${u.valor}`}
              <div class="unidad">
                <div class="que">
                  <span class="valor">{u.valor}</span>
                  {#if mapa[u.valor]}
                    {#if u.agregado}<span class="agregado">MÁS ESPECÍFICO</span>{/if}
                    {@render iab(mapa[u.valor], false)}
                  {:else if !varias && texto(c)}<div class="sig">{texto(c)}</div>{/if}
                </div>
                <div class="acc">
                  <Botones etiqueta={r.etiquetas[k]}
                    onveredicto={v => onveredicto(r, c.campo, u.valor, v)}
                    oncorreccion={t => oncorreccion(r, c.campo, u.valor, t)} />
                </div>
              </div>
            {/each}
            <div class="antes previo">
              <span>{c.original ? `El vendedor mandó: ${c.original}` : "El vendedor no mandó nada"}</span>
              <button class="bandera" class:activa={!!r.etiquetas[`_previo:${c.campo}|${c.original}`]} title="No debimos cambiarlo: lo correcto era lo que venía del vendedor"
                onclick={() => onveredicto(r, `_previo:${c.campo}`, c.original, r.etiquetas[`_previo:${c.campo}|${c.original}`] ? "" : "correcto")}>↩ Lo correcto era lo que venía antes</button>
            </div>
          </td>
        </tr>
      {/if}
    {/each}
    </tbody>
  </table>

  {#if r.extra}
    <div class="extra">
      <div class="ficha">
        <span><b>Opcional:</b> ¿la ficha IMDb <b>{tituloFicha}</b> es la misma obra que emite la app?</span>
        <Botones ficha etiqueta={r.etiquetas[`${FICHA}|${r.extra.imdb_id}`]}
          onveredicto={v => onveredicto(r, FICHA, r.extra.imdb_id, v)} oncorreccion={() => {}} />
      </div>
      <details>
        <summary>Información extra de IMDb / Wikidata <span class="sub">— referencia, no llena ninguna columna</span></summary>
        <dl>
          {#each ETIQ_EXTRA as [k, n]}{#if valorExtra(k)}<dt>{n}</dt><dd>{valorExtra(k)}</dd>{/if}{/each}
          {#each ETIQ_WD as [k, n]}{#if r.extra.wikidata?.[k]}<dt>{n}</dt><dd>{r.extra.wikidata[k]}</dd>{/if}{/each}
        </dl>
        {#if r.extra.ligero}<p class="sub">Fuera de la muestra solo se muestra lo que trae el CSV (sin caché de IMDb/Wikidata).</p>{/if}
      </details>
    </div>
  {/if}

  {#if mostrarFila && r.crudo}
    <details class="extra">
      <summary>Fila completa del CSV <span class="sub">— todas las columnas</span></summary>
      <dl>{#each Object.entries(r.crudo) as [k, v]}<dt>{k}</dt><dd>{v === "" || v === null ? "—" : v}</dd>{/each}</dl>
    </details>
  {/if}

  <div class="notas">
    <input type="text" placeholder="Notas (opcional)" value={r.nota} oninput={ev => onnota(r, ev.currentTarget.value)} />
  </div>
</section>

<style>
  .tarjeta { scroll-margin-top: 140px; background: var(--card); border: 1px solid var(--line); border-radius: 10px; margin-bottom: 14px; overflow: hidden; }
  .tarjeta.completa { border-color: var(--ok); }
  .cabeza { padding: 12px 14px; border-bottom: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: 4px 14px; align-items: baseline; }
  .num { color: var(--ink2); font-variant-numeric: tabular-nums; }
  .titulo { font-size: 17px; font-weight: 700; word-break: break-word; }
  .chip { font-size: 11px; font-weight: 700; padding: 1px 6px; border-radius: 3px; background: var(--accent); color: #fff; }
  .contexto { color: var(--ink2); font-size: 13px; width: 100%; word-break: break-word; }
  .enlaces { font-size: 13px; width: 100%; }
  table { width: 100%; border-collapse: collapse; }
  td { padding: 8px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
  tr:last-child td { border-bottom: 0; }
  td.campo { width: 170px; color: var(--ink2); font-size: 13px; }
  tr.llenado td { background: var(--fill-bg); }
  tr.llenado td.campo { border-left: 4px solid var(--fill-line); color: var(--fill-ink); font-weight: 600; }
  tr.corregido td { background: var(--fix-bg); }
  tr.corregido td.campo { border-left-color: var(--fix-line); color: var(--fix-ink); }
  tr.corregido .etiqueta { background: var(--fix-line); }
  tr.corregido .unidad { border-top-color: var(--fix-line); }
  tr.corregido .previo span { color: var(--fix-ink); font-weight: 600; }
  .etiqueta { display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: .03em; padding: 1px 6px; border-radius: 3px; background: var(--fill-line); color: #fff; margin-left: 4px; vertical-align: 1px; }
  .valor { font-weight: 600; word-break: break-word; }
  .vacio { color: var(--empty); font-style: italic; font-weight: 400; }
  .sig { color: var(--ink2); font-size: 13px; margin-top: 2px; }
  .cod { font-family: ui-monospace, Consolas, monospace; font-size: 12px; background: var(--line); padding: 0 4px; border-radius: 3px; color: var(--ink); }
  .en { opacity: .8; }
  .antes { color: var(--ink2); font-size: 12px; margin-top: 2px; }
  .original { display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: flex-start; justify-content: space-between; }
  .bandera { padding: 2px 8px; font-size: 12px; color: var(--ink2); }
  .bandera.activa { background: var(--bad-bg); border-color: var(--bad); color: var(--bad); font-weight: 700; }
  .previo { display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; justify-content: space-between; margin-top: 6px; }
  .correccion { display: block; margin-top: 6px; width: 220px; max-width: 100%; }
  .unidad { padding: 8px 0; border-top: 1px dashed var(--fill-line); display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: flex-start; justify-content: space-between; }
  .unidad:first-of-type { border-top: 0; padding-top: 2px; }
  .que { flex: 1 1 260px; min-width: 0; }
  .acc { flex: 0 0 auto; max-width: 100%; }
  .agregado { display: inline-block; font-size: 11px; font-weight: 700; padding: 1px 6px; border-radius: 3px; background: var(--accent); color: #fff; margin-left: 6px; vertical-align: 1px; }
  .extra { margin: 0; padding: 10px 14px; border-top: 1px solid var(--line); background: var(--bg); }
  .extra summary { cursor: pointer; font-weight: 600; font-size: 14px; }
  .sub { color: var(--ink2); font-size: 12px; font-weight: 400; }
  .extra dl { display: grid; grid-template-columns: 200px 1fr; gap: 4px 12px; margin: 10px 0 6px; font-size: 13px; }
  .extra dt { color: var(--ink2); word-break: break-word; }
  .extra dd { margin: 0; word-break: break-word; }
  .extra details { margin-top: 8px; }
  .ficha { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 13px; }
  .notas { padding: 10px 14px; border-top: 1px solid var(--line); }
  .notas input { width: 100%; }
  @media (max-width: 720px) {
    td { display: block; width: auto !important; border-bottom: 0; padding: 4px 14px; }
    tr { display: block; border-bottom: 1px solid var(--line); padding: 6px 0; }
    .extra dl { grid-template-columns: 1fr; }
    .extra dt { margin-top: 4px; }
  }
</style>
