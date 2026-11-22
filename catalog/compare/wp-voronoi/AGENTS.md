# US State Department Voronoi

Polygons extended over water from U.S. Department of State World Polygons, full-resolution layer, with Large Scale International Boundaries (LSIB) lines. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/wp-voronoi/wp_voronoi.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/wp-voronoi/wp_voronoi.pmtiles`, layer `wp_voronoi`
- Columns: every source attribute as published, plus `geometry`. Country code: `GENC_3` (GENC three-letter code, null for 2 of 323 rows). Name: `WP_Name`
- 323 polygons, the cleaned polygons extended over water and gaps (topo-tools edge-extend) to cover the whole globe

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/wp-voronoi/wp_voronoi.parquet' LIMIT 10;
```

## License

Terms set by the publisher at https://geodata.state.gov. Attribution: U.S. Department of State.
