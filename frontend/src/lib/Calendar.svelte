<script lang="ts">
    import {Calendar, Interaction, TimeGrid} from '@event-calendar/core'
    import {user} from "./stores/auth.js"
    import {makeRequest} from "./api"
    import type Presence from "../types/presence"
    import {onDestroy} from "svelte"
    import Switch from './Switch.svelte'
    
    const usernameToColor = username => {
        let hash = 0
        for (let i = 0 ; i < username.length ; i++) {
            hash = username.charCodeAt(i) + ((hash << 7) - hash)
        }

        const hue = Math.abs(hash) % 360

        // Use high saturation and moderate/dark lightness for contrast with white
        const saturation = 70 // %
        const lightness = 40 // %

        return `hsl(${hue}, ${saturation}%, ${lightness}%)`
    }

    const createCalendarEvent = async ({start, end}: { start: Date, end: Date }) =>
        await makeRequest('/presence', 'POST', {
            body: { start: start.toISOString(), end: end.toISOString() }
        })

    const updateCalendarEvent = async (event_id: number, {start, end}: { start: Date, end: Date }) =>
        await makeRequest(`/presence/${event_id}`, 'PUT', {
            body: { start: start.toISOString(),  end: end.toISOString() }
        })

    const deleteCalendarEvent = async (eventId: number) =>
        await makeRequest(`/presence/${eventId}`, 'DELETE')

    const fetchCalendarEvents = async ({start, end}: { start: Date, end: Date }) =>
        await makeRequest(`/presence${displayOnlySelf ? "/me" : ""}?start=${start.toISOString()}&end=${end.toISOString()}`)

    const fetchPresenceToEvents = async ({start, end, startStr, endStr}, successCallback, failureCallback) => {
        if (!$user) return []

        const res = await fetchCalendarEvents({start, end})
        if (!res.ok) failureCallback()

        const events: Presence[] = await res.json()
        return events.map(ev => ({
            start: new Date(ev.start),
            end: new Date(ev.end),
            title: ev.user.id === $user.id ? 'You' : ev.user.username,
            backgroundColor: usernameToColor(ev.user.username),
            resourceId: ev.id,
            editable: ev.user.id === $user.id,
            startEditable: ev.user.id === $user.id,
            durationEditable: ev.user.id === $user.id,
        }))
    }

    const eventClickHandler = async ({el, event, jsEvent, view}) => {
        if (!$user) return
        if (!event.editable) return
        if (event.resourceIds.length <= 0) {
            console.error('No resource id', event)
        }

        const res = await deleteCalendarEvent(event.resourceIds[0])
        if (!res.ok) return
        ec.removeEventById(event.id)
    }

    const eventDropHandler = async (
        {oldEvent, oldResource, newResource, delta, revert, jsEvent, view}
    ) => {
        if (!$user) revert()
        if (oldEvent.resourceIds.length <= 0) revert()

        const eventId = oldEvent.resourceIds[0]
        try {
            const start = new Date(oldEvent.start.getTime() + delta.seconds * 1000)
            const end = new Date(oldEvent.end.getTime() + delta.seconds * 1000)
            const res = await updateCalendarEvent(eventId, {start, end})
            if (!res.ok) {
                revert()
                return
            }
        }
        catch (e) {
            revert()
            console.error(e)
        }
    }

    const eventResizeHandler = async (
        {event, oldEvent, startDelta, endDelta, revert, jsEvent, view}
    ) => {
        if (!$user) revert()
        if (oldEvent.resourceIds.length <= 0) revert()

        const eventId = oldEvent.resourceIds[0]
        try {
            const start = new Date(oldEvent.start.getTime() + startDelta.seconds * 1000)
            const end = new Date(oldEvent.end.getTime() + endDelta.seconds * 1000)
            const res = await updateCalendarEvent(eventId, {start, end})
            if (!res.ok) {
                revert()
                return
            }
        }
        catch (e) {
            revert()
            console.error(e)
        }
    }

    const eventSelectHandler = async (
        {start, end, startStr, endStr, allDay, jsEvent, view, resource}
    ) => {
        if (!$user) {
            ec.unselect()
            return
        }

        const res = await createCalendarEvent({start, end})
        if (!res.ok) {
            ec.unselect()
            return
        }
        ec.unselect()
        ec.refetchEvents()
    }

    let displayOnlySelf: boolean = $state(false)
    let ec = $state()
    let options = $state({
        view: 'timeGridWeek',
        allDaySlot: false,
        pointer: true,
        nowIndicator: true,
        selectable: true,
        eventSources: [{ events: fetchPresenceToEvents }],
        eventClick: eventClickHandler,
        eventDrop: eventDropHandler,
        eventResize: eventResizeHandler,
        select: eventSelectHandler,
        eventBackgroundColor: usernameToColor($user?.username ?? 'you'),
    })

    const userUnsubscribe = user.subscribe(($user) => {
        if ($user) {
            options = {
                ...options,
                eventBackgroundColor: usernameToColor($user.username ?? 'you'),
            }
        }
    })
    onDestroy(userUnsubscribe)

    function handleSwitchChange() {
        displayOnlySelf = !displayOnlySelf
        ec.refetchEvents()
    }

</script>

{#if $user}
    <Switch
        value={displayOnlySelf}
        label="Only display your events"
        design="slider"
        onclick={handleSwitchChange}
    />
    <Calendar bind:this={ec} plugins={[TimeGrid, Interaction]} {options} />
{/if}