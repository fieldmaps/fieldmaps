# US State Department World Polygons

U.S. Department of State World Polygons, full-resolution layer. Shown on the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/wp-polygons/wp_polygons.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/wp-polygons/wp_polygons.pmtiles`, layer `wp_polygons`
- Columns: `iso3` (VARCHAR, GENC three-letter code, null for 2 rows), `name` (VARCHAR), `geometry` (geometry, `OGC:CRS84`)

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/wp-polygons/wp_polygons.parquet' LIMIT 10;
```

## License

Terms set by the publisher at https://geodata.state.gov. Attribution: U.S. Department of State.
