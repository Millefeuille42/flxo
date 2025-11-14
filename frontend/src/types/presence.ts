import type User from "./user";

export default interface Presence {
    start: string
    end: string
    id: number
    user: User
}
