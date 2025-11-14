import { writable } from 'svelte/store';

export const jwt = writable<string | null>(null)
export const user = writable<any>(null)
