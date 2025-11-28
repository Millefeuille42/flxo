<script lang="ts">
  import viteLogo from '/vite.svg'
  import { onMount } from 'svelte'

  import { jwt } from './lib/stores/auth';
  import { get } from 'svelte/store';
  import Username from "./lib/Username.svelte";
  import Calendar from "./lib/Calendar.svelte";
  import type User from "./types/user";
  import {makeRequest} from "./lib/api";

  let token: string | null = $state(get(jwt))
  let user: User | undefined = undefined

  onMount(async () => {
    console.log("App: mounted")
    if (get(jwt)) {
      makeRequest('/user/me').catch(e => {
        localStorage.removeItem('jwt')
        token = null
        jwt.set(null)
        throw e
      })
    }
    console.log("App: no JWT found. Querying...")

    const isLocal =
            location.hostname === "localhost" ||
            location.hostname === "127.0.0.1"

    const urlParams = new URLSearchParams(window.location.search);
    const fromStorage = localStorage.getItem("jwt") ?? '';
    const code: string = urlParams.get('code') ?? '';
    const state: string = urlParams.get('state') ?? '';

    if (fromStorage) {
      console.log("App: using token from local storage")
      jwt.set(fromStorage)
      token = get(jwt)
    } else if (code && state) {
      console.log("App: got code from SSO")
      const res = await makeRequest(`/auth/oauth2/callback?code=${code}&state=${state}`)
      if (!res.ok) console.log("Invalid response from SSO: ", await res.text())
      console.log("App: using token from backend")
      jwt.set((await res.json()).access_token)
    } else if (import.meta.env.DEV && import.meta.env.VITE_DEV_JWT_NON_LOCAL && !isLocal) {
      console.log("App: using non-local dev JWT")
      jwt.set(import.meta.env.VITE_DEV_JWT_NON_LOCAL)
    } else if (import.meta.env.DEV && import.meta.env.VITE_DEV_JWT) {
      console.log("App: using dev JWT")
      jwt.set(import.meta.env.VITE_DEV_JWT)
    }

    token = get(jwt)
    localStorage.setItem('jwt', token ?? '')
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
