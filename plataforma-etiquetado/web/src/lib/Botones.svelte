<script lang="ts">
  import type { Etiqueta } from "./api";

  let { etiqueta, ficha = false, onveredicto, oncorreccion }: {
    etiqueta: Etiqueta | undefined; ficha?: boolean;
    onveredicto: (v: string) => void; oncorreccion: (texto: string) => void;
  } = $props();

  const opciones = $derived([
    ["correcto", ficha ? "✓ Sí, es la misma" : "✓ Correcto"],
    ["incorrecto", ficha ? "✗ No, es otra" : "✗ Incorrecto"],
    ["no_se_sabe", "? No se sabe"],
  ]);
</script>

<div class="botones">
  {#each opciones as [cod, txt] (cod)}
    <button class={etiqueta?.veredicto === cod ? "sel-" + cod : ""} onclick={() => onveredicto(etiqueta?.veredicto === cod ? "" : cod)}>{txt}</button>
  {/each}
</div>
{#if etiqueta?.veredicto === "incorrecto" && !ficha}
  <input type="text" class="correccion" placeholder="valor correcto (opcional)" value={etiqueta.correcto}
    oninput={ev => oncorreccion(ev.currentTarget.value)} />
{/if}

<style>
  .botones { display: flex; gap: 6px; flex-wrap: wrap; }
  @media (min-width: 721px) { .botones { flex-wrap: nowrap; } }
  .botones button { padding: 4px 10px; font-size: 13px; }
  .sel-correcto { background: var(--ok-bg); border-color: var(--ok); color: var(--ok); font-weight: 700; }
  .sel-incorrecto { background: var(--bad-bg); border-color: var(--bad); color: var(--bad); font-weight: 700; }
  .sel-no_se_sabe { background: var(--unk-bg); border-color: var(--unk); color: var(--unk); font-weight: 700; }
  .correccion { margin-top: 6px; width: 100%; }
</style>
