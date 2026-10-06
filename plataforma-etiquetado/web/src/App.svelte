<script lang="ts">
  import { api, type Ambito, type Opciones, type Usuario } from "./lib/api";
  import Login from "./lib/Login.svelte";
  import Revision from "./lib/Revision.svelte";
  import Resultados from "./lib/Resultados.svelte";

  type Vista = Ambito | "resultados";
  let yo = $state<Usuario | null>(null);
  let cargando = $state(true);
  let opciones = $state<Opciones | null>(null);
  let vista = $state<Vista>(leerVista());

  function leerVista(): Vista {
    const h = location.hash.slice(1);
    return h === "completo" || h === "resultados" ? h : "muestra";
  }
  $effect(() => { history.replaceState(null, "", "#" + vista); });
  $effect(() => { if (yo && yo.rol !== "admin") vista = "muestra"; });

  async function iniciar() {
    try {
      yo = await api<Usuario>("/api/yo");
      opciones = await api<Opciones>("/api/opciones");
    } catch { yo = null; }
    cargando = false;
  }
  async function salir() {
    await api("/api/logout", { metodo: "POST" }).catch(() => {});
    yo = null; opciones = null;
  }
  iniciar();
</script>

{#if cargando}
  <p class="centro">Cargando…</p>
{:else if !yo}
  <Login onentrar={iniciar} />
{:else if opciones}
  <nav>
    <div class="wrap fila">
      <strong class="marca">🏷️ Etiquetas CTV</strong>
      <div class="pestanas">
        <button class:activa={vista === "muestra"} onclick={() => (vista = "muestra")}>Muestra ({opciones.tarjetas_muestra})</button>
        {#if yo.rol === "admin"}
          <button class:activa={vista === "completo"} onclick={() => (vista = "completo")}>Datos completos</button>
          <button class:activa={vista === "resultados"} onclick={() => (vista = "resultados")}>Resultados</button>
        {/if}
      </div>
      <span class="quien">{yo.nombre} · {yo.rol === "admin" ? "administración" : "revisión de la muestra"}
        <button onclick={salir}>Salir</button></span>
    </div>
  </nav>
  {#if vista === "resultados"}
    <Resultados />
  {:else}
    {#key vista}
      <Revision ambito={vista} {opciones} admin={yo.rol === "admin"} />
    {/key}
  {/if}
{/if}

<style>
  .centro { text-align: center; margin-top: 20vh; color: var(--ink2); }
  nav { background: var(--card); border-bottom: 1px solid var(--line); padding: 8px 16px; }
  .fila { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; }
  .marca { font-size: 16px; }
  .pestanas { display: flex; gap: 4px; flex-wrap: wrap; flex: 1 1 auto; }
  .pestanas button { border-color: transparent; background: none; }
  .pestanas button.activa { background: var(--bg); border-color: var(--line); font-weight: 700; }
  .quien { color: var(--ink2); font-size: 13px; display: flex; gap: 8px; align-items: center; }
  .quien button { padding: 3px 10px; font-size: 13px; }
</style>
