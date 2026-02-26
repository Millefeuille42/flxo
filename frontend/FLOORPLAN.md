# Floor Plan SVG Requirements

The floor plan is an SVG file served as a static asset and referenced via `floor_plan_url` in the backend config (`config.toml` `[app]` section). The frontend fetches it at runtime and injects it inline to manipulate desk elements.

## Desk count configuration

The number of desks is configured via `desk_count` in the backend config (`[app]` section or `FLXO__APP__DESK_COUNT` env var). The frontend reads it from `GET /auth/config` and generates desk IDs `desk1`..`deskN` accordingly.

## Required desk IDs

Each bookable desk must be an SVG element (typically a `<rect>`, `<path>`, or `<g>`) with an `id` matching `desk1` through `deskN` (where N = `desk_count`):

```
desk1, desk2, ..., deskN
```

These IDs are used to:
- Detect clicks (assign a desk to a user)
- Change `fill` / `fillOpacity` to show occupancy colors
- Apply hover effects (`brightness`, `drop-shadow`)

If an ID is missing from the SVG, the corresponding desk is silently ignored (no error, but the desk won't be interactive).

## Optional screen IDs

Elements with IDs starting with `screen` (e.g. `screen1`, `screen2`) are togglable via the monitor icon button in the sidebar floor plan. They are hidden by default with the CSS rule `[id^="screen"] { display: none }`.

## Sizing

The SVG should define a `viewBox` for proper scaling. The frontend constrains it with:
- Sidebar (`FloorPlan.vue`): `max-height: 300px`, full width of sidebar (280px)
- Modal (`DeskPickerModal.vue`): `max-height: 60vh`, up to 700px wide

## Adding or removing desks

1. Update `desk_count` in `config.toml` `[app]` section.
2. Update the SVG to include/remove the matching `id` elements (`desk1`..`deskN`).
3. The backend will auto-create missing `Seat` records on first load (see `initApp` in `src/state.js`).

## Example minimal SVG

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect id="desk1" x="50"  y="50"  width="80" height="60" fill="#d8d8d8" />
  <rect id="desk2" x="200" y="50"  width="80" height="60" fill="#d8d8d8" />
  <rect id="desk3" x="350" y="50"  width="80" height="60" fill="#d8d8d8" />
  <rect id="desk4" x="50"  y="200" width="80" height="60" fill="#d8d8d8" />
  <rect id="desk5" x="200" y="200" width="80" height="60" fill="#d8d8d8" />
  <rect id="desk6" x="350" y="200" width="80" height="60" fill="#d8d8d8" />
</svg>
```
