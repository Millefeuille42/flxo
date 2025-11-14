<script lang="ts">
    import {onMount} from "svelte";
    import {get} from "svelte/store";
    import {jwt, user} from "./stores/auth";
    import type {User} from "../types/user";
    import {API_URL} from "./constants";

    let currentUser: User | null = $state(get(user))

    onMount(async () => {
        if (currentUser) return
        const res = await fetch(API_URL + '/user/me', {
            credentials: 'include',
            headers: {
                Authorization: `Bearer ${get(jwt)}`
            }
        })
        if (!res.ok) return
        currentUser = await res.json()
        user.set(currentUser)
    })
</script>

<p> {currentUser?.username ?? "not logged in"}</p>