# Boundary comparison

Global ADM0 polygons from other publishers, tiled for the comparison page at https://fieldmaps.io/international/compare/. The FieldMaps polygons shown on that page come from `fieldmaps/international` (`odbl/humanitarian/adm0-polygons`).

## Collections

- `wp-polygons`: US State Department World Polygons, full-resolution layer.

Each collection holds one GeoParquet (`<id>_polygons.parquet`) and its PMTiles (`<id>_polygons.pmtiles`, layer `<id>_polygons`, zooms 0 to 12).

## Data access

- Base URL: `https://data.source.coop/fieldmaps/site/compare/`
- Columns: every column the source publishes, plus `geometry`. Each collection's AGENTS.md names its country code and name columns.
- GeoParquet V2, CRS `OGC:CRS84`, clipped to ±180° longitude and ±90° latitude, at the source's full resolution. Polygons form a clean coverage (topo-tools topo-clean), with coordinates rounded to 1e-9 degrees.

```sql
LOAD spatial;
SELECT GENC_3, WP_Name
FROM 'https://data.source.coop/fieldmaps/site/compare/wp-polygons/wp_polygons.parquet';
```

## License

Each collection carries its source's license and attribution in its README.
