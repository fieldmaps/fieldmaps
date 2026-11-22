# Boundary comparison

Global ADM0 boundaries from other publishers, tiled for the comparison page at https://fieldmaps.io/international/compare/. The FieldMaps polygons and lines shown on that page come from `fieldmaps/international` (`odbl/humanitarian/adm0-polygons`, `adm0-lines`); its Voronoi is `fieldmaps-voronoi` here.

## Collections

Sources, in the page's order: `wp` (US State Department), `overture` (Overture Maps Divisions), `wb` (World Bank Official Boundaries), `gaul` (FAO GAUL 2025), `gadm` (GADM 4.1), `cgaz` (geoBoundaries CGAZ), `ne` (Natural Earth). Each source has up to three collections:

- `<id>-polygons`: the source's ADM0 polygons, topology-cleaned.
- `<id>-lines`: international boundary lines. `wp` uses LSIB and `overture` its `division_boundary` lines; the others are the shared edges of the cleaned polygons, with the country on each side.
- `<id>-voronoi`: the polygons extended over water and gaps to cover the globe (topo-tools edge-extend).

`attributes` holds one table, not a layer: each source's ADM0 names, labels, sovereigns, statuses and regions side by side, one row per ISO3 code, with UN M49 and UNTERM as references (`attributes.json` and `attributes.parquet`).

Each collection holds one GeoParquet (`<id>_<kind>.parquet`) and its PMTiles (`<id>_<kind>.pmtiles`, layer `<id>_<kind>`, zooms 0 to 12). Each collection's AGENTS.md lists its columns and license.

## Data access

- Base URL: `https://data.source.coop/fieldmaps/site/compare/`
- Columns: every column the source publishes, plus `geometry`. Each collection's AGENTS.md names its country code and name columns.
- GeoParquet V2, CRS `OGC:CRS84`, clipped to ±180° longitude and ±90° latitude, at the source's full resolution. Lines have `line_type` (`international`, `armistice`, `special`). Polygons form a clean coverage (topo-tools topo-clean), with coordinates rounded to 1e-9 degrees.

```sql
LOAD spatial;
SELECT GENC_3, WP_Name
FROM 'https://data.source.coop/fieldmaps/site/compare/wp-polygons/wp_polygons.parquet';
```

## License

Each collection carries its source's license and attribution in its README.
