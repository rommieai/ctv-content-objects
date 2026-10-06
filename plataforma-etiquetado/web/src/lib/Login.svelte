<script lang="ts">
  import { api } from "./api";

  let { onentrar }: { onentrar: () => void } = $props();
  let usuario = $state("");
  let clave = $state("");
  let error = $state("");
  let enviando = $state(false);

  async function entrar(ev: SubmitEvent) {
    ev.preventDefault();
    enviando = true; error = "";
    try {
      await api("/api/login", { metodo: "POST", cuerpo: { usuario, clave } });
      onentrar();
    } catch (e) {
      error = (e as Error).message;
    }
    enviando = false;
  }
</script>

<main>
  <form onsubmit={entrar}>
    <h1>🏷️ Etiquetas CTV</h1>
    <p>Revisión manual del relleno de content objects</p>
    <label>Usuario <input type="text" bind:value={usuario} autocomplete="username" required /></label>
    <label>Contraseña <input type="password" bind:value={clave} autocomplete="current-password" required /></label>
    {#if error}<div class="error">{error}</div>{/if}
    <button class="primario" disabled={enviando}>{enviando ? "Entrando…" : "Entrar"}</button>
  </form>
</main>

<style>
  main { min-height: 100vh; display: grid; place-items: center; padding: 16px; }
  form { width: 100%; max-width: 340px; background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 24px; display: grid; gap: 12px; }
  h1 { margin: 0; font-size: 20px; }
  p { margin: 0 0 4px; color: var(--ink2); font-size: 13px; }
  label { display: grid; gap: 4px; font-size: 13px; color: var(--ink2); }
  .error { background: var(--bad-bg); color: var(--bad); padding: 6px 10px; border-radius: 6px; font-size: 13px; }
</style>
