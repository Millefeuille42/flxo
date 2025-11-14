<script lang="ts">
  import viteLogo from '/vite.svg'
  import { onMount } from 'svelte'

  import { jwt } from './lib/stores/auth';
  import { get } from 'svelte/store';
  import Username from "./lib/Username.svelte";
  import Calendar from "./lib/Calendar.svelte";
  import type User from "./types/user";

  let token: string | null = $state(get(jwt))
  let user: User | undefined = undefined

  onMount(async () => {
    console.log("App: mounted")
    if (get(jwt)) return
    console.log("App: no JWT found. Querying...")

    const isLocal =
            location.hostname === "localhost" ||
            location.hostname === "127.0.0.1"
    if (import.meta.env.DEV && import.meta.env.VITE_DEV_JWT_NON_LOCAL && !isLocal) {
      console.log("App: using non-local dev JWT")
      jwt.set(import.meta.env.VITE_DEV_JWT_NON_LOCAL)
      token = get(jwt)
      return
    }

    if (import.meta.env.DEV && import.meta.env.VITE_DEV_JWT) {
      console.log("App: using dev JWT")
      jwt.set(import.meta.env.VITE_DEV_JWT)
      token = get(jwt)
      return
    }
    // TODO write normal auth route
  })

</script>

<main>
  {#if !token}
    <div>
      <img src={viteLogo} class="logo" alt="Vite Logo" />
    </div>
    <h1>Welcome to {import.meta.env.VITE_APPLICATION_NAME}</h1>
  {/if}

  <div class="card">
    {#if !token}
      <form method="get" action="{import.meta.env.VITE_BACKEND_URL}/auth/oauth2">
        <input type="submit" value="Login with {import.meta.env.VITE_COMPANY_NAME} SSO" />
      </form>
    {:else}
      <Username/>
      <Calendar/>
    {/if}
  </div>


  <p class="footer">
    Made with {#if import.meta.env.DEV}🚧{:else}❤️{/if} by
    <a rel="noreferrer" target="_blank" href="https://github.com/millefeuille42">Millefeuille</a>
  </p>
</main>

<style>
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }

  .footer {
    color: #888;
  }
</style>
