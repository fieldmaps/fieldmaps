# FieldMaps

Static site for [fieldmaps.io](https://fieldmaps.io), built with [Astro](https://astro.build) and Svelte, deployed to Cloudflare Workers Static Assets. It presents the [international](https://source.coop/fieldmaps/international) and [subnational](https://source.coop/fieldmaps/subnational) boundary datasets on Source Cooperative.

## Developing

```bash
npm install
npm run dev
```

## Checks

```bash
npm run check
npm run lint
```

## Building

```bash
npm run build
npm run preview   # serves dist/ with wrangler, applying _redirects and the 404 page
```
