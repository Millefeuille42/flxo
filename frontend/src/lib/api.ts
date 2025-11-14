import {jwt} from "./stores/auth.js"
import {get} from "svelte/store";
import {API_URL} from "./constants";


export const makeRequest = async (
    endpoint: string, method: string = "GET", options: { headers?: Record<string, string>; body?: any } = {}
) => {
    const { headers = {}, body = {} } = options;

    const fetchOptions: RequestInit = {
        method,
        credentials: 'include',
        headers: {
            ...headers,
            'Content-Type': 'application/json',
            Authorization: `Bearer ${get(jwt)}`
        }
    };

    if (method !== "GET" && method !== "HEAD") {
        fetchOptions.body = JSON.stringify(body);
    }

    return await fetch(`${API_URL}${endpoint}`, fetchOptions);
}