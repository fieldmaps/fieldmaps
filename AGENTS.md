# AGENTS.md

Astro 7 static site + Svelte 5 islands (runes), MapLibre GL + PMTiles. Deployed by Cloudflare Workers Builds from `wrangler.jsonc` (assets in `./dist`).

## Routes

- `/`, `/international/`, `/international/methodology/`, `/explore/`, `/subnational/`, `/subnational/methodology/`
- Legacy paths redirect via `public/_redirects`.

## Data

Read directly from Source Cooperative (`https://data.source.coop/fieldmaps/{international,subnational,site}/...`), which serves CORS `*` and HTTP range requests.

- `catalog/` is the Portolan catalog for `fieldmaps/site`, the story demo layers. `uv run python scripts/build.py` runs `scripts/*-steps.sql`, builds PMTiles, then `portolan add` and `check`; `--push` syncs it with `scripts/fieldmaps_publish.py` (byte-identical with `fieldmaps/international`). Pushing needs `.env` from `.env.example` and the AWS CLI.

## Commands

- `npm run check && npm run lint && npm run build` before every commit.
- `npm run preview` serves `dist/` through wrangler to test redirects and 404 handling.
- `typescript` stays on 6.x until `@astrojs/check` accepts 7.
- `$lib` aliases `src/lib`.
