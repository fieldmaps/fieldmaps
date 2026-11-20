# CLAUDE.md

Astro 7 static site + Svelte 5 islands (runes), MapLibre GL + PMTiles. Deployed by Cloudflare Workers Builds from `wrangler.jsonc` (assets in `./dist`).

## Routes

- `/`, `/international/`, `/international/methodology/`, `/subnational/`, `/subnational/methodology/`
- Legacy paths redirect to `/` via `public/_redirects`.

## Data

Read directly from Source Cooperative (`https://data.source.coop/fieldmaps/{international,subnational}/...`), which serves CORS `*` and HTTP range requests.

## Commands

- `npm run check && npm run lint && npm run build` before every commit.
- `npm run preview` serves `dist/` through wrangler to test redirects and 404 handling.
- `typescript` stays on 6.x until `@astrojs/check` accepts 7.
- `$lib` aliases `src/lib`.
