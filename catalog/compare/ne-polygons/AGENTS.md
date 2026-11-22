# Natural Earth

Natural Earth 1:10m Admin 0 Countries. Prepared for the boundary comparison page on fieldmaps.io.

## Data access

- GeoParquet: `https://data.source.coop/fieldmaps/site/compare/ne-polygons/ne_polygons.parquet`
- PMTiles: `https://data.source.coop/fieldmaps/site/compare/ne-polygons/ne_polygons.pmtiles`, layer `ne_polygons`
- Columns: every source attribute as published, plus `geometry`. Country code: `ADM0_A3` (Natural Earth's three-letter code). Name: `NAME`
- 258 polygons forming a clean coverage (no gaps or overlaps up to 1e-8 degrees), with coordinates rounded to 1e-9 degrees

```sql
LOAD spatial;
SELECT * FROM 'https://data.source.coop/fieldmaps/site/compare/ne-polygons/ne_polygons.parquet' LIMIT 10;
```

## License

Public domain. Attribution: Natural Earth.
