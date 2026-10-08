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
    <h1>CTV by <b>TagScreen</b></h1>
    <p>Revisión manual del relleno de content objects</p>
    <label>Usuario <input type="text" bind:value={usuario} autocomplete="username" required /></label>
    <label>Contraseña <input type="password" bind:value={clave} autocomplete="current-password" required /></label>
    {#if error}<div class="error">{error}</div>{/if}
    <button class="primario" disabled={enviando}>{enviando ? "Entrando…" : "Entrar"}</button>
  </form>
</main>

<style>
  main { min-height: 100vh; display: grid; place-items: center; padding: 16px; }
  form { width: 100%; max-width: 340px; background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 24px; display: grid; gap: 12px; box-shadow: 0 0 20px 5px rgba(163, 87, 250, .18), 0 5px 5px rgba(0, 0, 0, .25); }
  h1 { margin: 0; font-size: 20px; font-weight: 300; color: var(--ink2); }
  h1 b { font-weight: 800; color: transparent; background: linear-gradient(90deg, #a357fa, #d9c8fa 67%); -webkit-background-clip: text; background-clip: text; }
  p { margin: 0 0 4px; color: var(--ink2); font-size: 13px; }
  label { display: grid; gap: 4px; font-size: 13px; color: var(--ink2); }
  .error { background: var(--bad-bg); color: var(--bad); padding: 6px 10px; border-radius: 6px; font-size: 13px; }
</style>
